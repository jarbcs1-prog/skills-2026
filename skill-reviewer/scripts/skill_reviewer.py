"""Deterministic review engine for agent skill packages.

Evaluates a skill directory (SKILL.md plus bundled resources) on six
dimensions - description, structure, workflow, resources, safety and tests -
totalling 100 points, mirroring the spirit of the skill-judge D1-D8 model
without importing it.
"""

from __future__ import annotations

import re
from pathlib import Path

DIMENSIONS: dict[str, int] = {
    "description": 20,
    "structure": 20,
    "workflow": 15,
    "resources": 15,
    "safety": 10,
    "tests": 20,
}

REQUIRED_SECTIONS: list[str] = [
    "Description",
    "When to use",
    "Workflow",
    "Input",
    "Output",
    "Notes",
]

PASS_THRESHOLD = 70

SECRET_PATTERNS: dict[str, re.Pattern[str]] = {
    "openai_key": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    "password": re.compile(r"password\s*[=:]\s*['\"][^'\"]{6,}", re.IGNORECASE),
    "api_key": re.compile(r"api_key\s*[=:]", re.IGNORECASE),
    "token": re.compile(r"token\s*[=:]\s*['\"][A-Za-z0-9]{16,}", re.IGNORECASE),
    "aws_secret": re.compile(r"aws_secret", re.IGNORECASE),
}

IGNORED_DIRS: set[str] = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".skill-reviewer",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}

STOPWORDS: set[str] = {
    "a",
    "about",
    "after",
    "against",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "before",
    "best",
    "but",
    "by",
    "can",
    "for",
    "from",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "no",
    "not",
    "of",
    "official",
    "on",
    "or",
    "over",
    "practice",
    "practices",
    "so",
    "than",
    "the",
    "then",
    "this",
    "to",
    "use",
    "using",
    "was",
    "when",
    "will",
    "with",
    "you",
    "your",
}


def _parse_frontmatter(content: str) -> dict[str, str]:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip().lower()] = value.strip()
    return fields


def _section_matches(content: str) -> set[str]:
    sections: set[str] = set()
    for line in content.splitlines():
        match = re.match(r"^##\s+([^#]+?)\s*$", line)
        if match:
            sections.add(match.group(1).strip().lower())
    return sections


def validate_structure(path: Path) -> dict:
    """Validate the structural requirements of a skill's SKILL.md."""
    skill_md = Path(path) / "SKILL.md"
    checks = {
        "frontmatter": False,
        "name": False,
        "description": False,
        "line_count": False,
        "sections": False,
    }
    errors = [f"SKILL.md not found in {Path(path)}"]
    if not skill_md.is_file():
        return {"valid": False, "checks": checks, "errors": errors, "score": 0}

    content = skill_md.read_text(encoding="utf-8", errors="ignore")
    frontmatter = _parse_frontmatter(content)
    line_count = len(content.splitlines())
    section_count = len(_section_matches(content) & {s.lower() for s in REQUIRED_SECTIONS})

    checks["frontmatter"] = content.startswith("---")
    checks["name"] = "name" in frontmatter
    checks["description"] = bool(frontmatter.get("description", "").strip())
    checks["line_count"] = 10 <= line_count <= 1000
    checks["sections"] = section_count >= 3

    labels = {
        "frontmatter": "Missing YAML frontmatter (SKILL.md must start with '---')",
        "name": "Missing 'name' field in frontmatter",
        "description": "Missing or empty 'description' field in frontmatter",
        "line_count": "SKILL.md must be between 10 and 1000 lines (found {})".format(line_count),
        "sections": "At least 3 required sections needed (found {})".format(section_count),
    }
    errors = [labels[key] for key in ("frontmatter", "name", "description", "line_count", "sections") if not checks[key]]

    score = round(sum(checks.values()) / len(checks) * DIMENSIONS["structure"])
    return {"valid": all(checks.values()), "checks": checks, "errors": errors, "score": score}


def score_description(frontmatter_description: str) -> int:
    """Score the frontmatter description on a 0-20 scale."""
    description = frontmatter_description.strip()
    if not description:
        return 0

    score = 0
    if len(description) >= 15:
        score += 5
    if re.search(r"\b(when|trigger|triggers)\b", description, re.IGNORECASE):
        score += 5
    words = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z-]*", description)]
    specific = [w for w in words if w not in STOPWORDS]
    if len(specific) >= 2:
        score += 5
    if not re.search(r"\bai\s+assistant\b|\byou\s+are\s+(?:an\s+)?ai\s+assistant\b", description, re.IGNORECASE):
        score += 5
    return score


def security_scan(path: Path) -> dict:
    """Scan every file under the skill directory for leaked-secret patterns."""
    root = Path(path)
    vulnerabilities: list[dict] = []
    for file in sorted(root.rglob("*")):
        if not file.is_file():
            continue
        relative = file.relative_to(root)
        if any(part in IGNORED_DIRS for part in relative.parts):
            continue
        try:
            lines = file.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for line_number, line in enumerate(lines, start=1):
            for pattern_name, pattern in SECRET_PATTERNS.items():
                if pattern.search(line):
                    vulnerabilities.append(
                        {"file": str(relative), "pattern": pattern_name, "line": line_number}
                    )
    return {"vulnerabilities": vulnerabilities}


def check_consistency(path: Path) -> dict:
    """Verify referenced files exist and that tests/ is present when mentioned."""
    root = Path(path)
    skill_md = root / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8", errors="ignore") if skill_md.is_file() else ""
    missing: list[str] = []

    for reference in re.findall(r"`([A-Za-z0-9_.\-/]+)`", content):
        if not reference.startswith(("scripts/", "references/", "assets/", "tests/")):
            continue
        if not (root / reference).exists():
            missing.append(reference)

    if re.search(r"\btest", content, re.IGNORECASE) and not (root / "tests").is_dir():
        missing.append("tests/")

    missing = sorted(set(missing))
    return {"missing_references": missing, "consistent": not missing}


def _score_workflow(content: str) -> int:
    if re.search(r"^##\s+workflow\s*$", content, re.IGNORECASE | re.MULTILINE):
        return DIMENSIONS["workflow"]
    if "workflow" in content.lower():
        return DIMENSIONS["workflow"] - 5
    if re.search(r"(^\d+\.\s|\bstep\s+\d)", content, re.IGNORECASE | re.MULTILINE):
        return 5
    return 0


def _score_resources(root: Path) -> int:
    score = 0
    for subdirectory in ("scripts", "references", "assets"):
        directory = root / subdirectory
        if directory.is_dir() and any(file.is_file() for file in directory.rglob("*")):
            score += 5
    return score


def _score_tests(root: Path) -> int:
    tests_dir = root / "tests"
    if not tests_dir.is_dir():
        return 0
    files = [file for file in tests_dir.rglob("*") if file.is_file()]
    if not files:
        return 10
    if any(file.suffix == ".py" for file in files):
        return DIMENSIONS["tests"]
    return 12


def generate_fixes(review: dict) -> list[str]:
    """Return actionable fix strings for a completed review."""
    fixes: list[str] = []
    if review.get("description_score", DIMENSIONS["description"]) < 14:
        fixes.append("Rewrite frontmatter description to include a trigger phrase ('Use when ...') and specific nouns")
    content = review.get("content", "")
    if "workflow" not in content.lower():
        fixes.append("Add a 'Workflow' section with numbered steps")
    for reference in review.get("consistency", {}).get("missing_references", []):
        fixes.append(f"Create missing file {reference} or remove its mention")
    structure = review.get("structure", {})
    if not structure.get("checks", {}).get("frontmatter", True):
        fixes.append("Add YAML frontmatter with name and description")
    return fixes


def review_skill(path: Path) -> dict:
    """Review a skill directory and produce the full review dict."""
    root = Path(path)
    skill_md = root / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8", errors="ignore") if skill_md.is_file() else ""

    structure = validate_structure(root)
    frontmatter = _parse_frontmatter(content)
    description_score = score_description(frontmatter.get("description", ""))
    security = security_scan(root)
    consistency = check_consistency(root)

    dimensions = {
        "description": description_score,
        "structure": structure["score"],
        "workflow": _score_workflow(content),
        "resources": _score_resources(root),
        "safety": DIMENSIONS["safety"] if not security["vulnerabilities"] else 0,
        "tests": _score_tests(root),
    }
    total = sum(dimensions.values())
    passed = total >= PASS_THRESHOLD and bool(structure["valid"]) and not security["vulnerabilities"]

    review: dict = {
        "path": str(root),
        "name": frontmatter.get("name", root.name),
        "score": total,
        "dimensions": dimensions,
        "structure": structure,
        "description_score": description_score,
        "security": security,
        "consistency": consistency,
        "content": content,
    }
    review["fixes"] = generate_fixes(review)
    review["passed"] = passed
    return review
