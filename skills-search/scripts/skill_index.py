"""Local skill registry indexing, search, dependency resolution and composition.

Standard-library only. Deterministic ordering is used everywhere.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

FRONTMATTER_DELIMITER = "---"
DEFAULT_VERSION = "0.0.0"

_KEY_RE = re.compile(r"^[a-z0-9_-]+:")
_STEP_RE = re.compile(r"^\s*\d+[.)]\s+(.*)$")
_TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass
class Skill:
    """Metadata for a skill package found in a registry directory."""

    name: str
    path: Path
    version: str
    description: str
    has_tests: bool
    frontmatter: dict[str, str] = field(default_factory=dict)


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse simple `key: value` frontmatter delimited by two `---` lines."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_DELIMITER:
        return {}
    fields: dict[str, str] = {}
    current: str | None = None
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == FRONTMATTER_DELIMITER:
            break
        if not stripped:
            continue
        if _KEY_RE.match(stripped):
            key, _, value = stripped.partition(":")
            current = key.strip().lower()
            fields[current] = "" if value.strip() in ("|", ">") else value.strip()
        elif current is not None:
            fields[current] += " " + stripped
    return {key: value.strip() for key, value in fields.items()}


def index_local_skills(root: Path) -> list[Skill]:
    """Index every directory under ``root`` that contains a SKILL.md file."""
    skills: list[Skill] = []
    for entry in sorted(root.iterdir(), key=lambda item: item.name):
        if not entry.is_dir():
            continue
        skill_file = entry / "SKILL.md"
        if not skill_file.is_file():
            continue
        frontmatter = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
        skills.append(
            Skill(
                name=frontmatter.get("name", entry.name),
                path=entry,
                version=frontmatter.get("version", DEFAULT_VERSION),
                description=frontmatter.get("description", ""),
                has_tests=(entry / "tests").is_dir(),
                frontmatter=frontmatter,
            )
        )
    skills.sort(key=lambda skill: skill.name)
    return skills


def tokenize(text: str) -> list[str]:
    """Lower-case alphanumeric tokens from ``text``."""
    return _TOKEN_RE.findall(text.lower())


def trigrams(text: str) -> set[str]:
    """All overlapping 3-character shingles of ``text`` (lower-cased)."""
    normalized = text.lower()
    return {normalized[index : index + 3] for index in range(max(0, len(normalized) - 2))}


def trigram_jaccard(first: str, second: str) -> float:
    """Jaccard similarity between the trigram sets of two strings."""
    first_trigrams = trigrams(first)
    second_trigrams = trigrams(second)
    if not first_trigrams and not second_trigrams:
        return 0.0
    return len(first_trigrams & second_trigrams) / len(first_trigrams | second_trigrams)


def search_skills(query: str, skills: list[Skill]) -> list[dict]:
    """Rank skills against ``query`` by a weighted name/description/path/trigram score."""
    query_tokens = set(tokenize(query))
    normalized_query = query.lower()
    ranked: list[tuple[float, Skill]] = []
    for skill in skills:
        name = skill.name.lower()
        path = str(skill.path).lower()
        score = 0.0
        if name == normalized_query or (query_tokens & set(tokenize(skill.name))):
            score += 3.0
        if query_tokens:
            overlap = len(query_tokens & set(tokenize(skill.description)))
            score += 2.0 * overlap / len(query_tokens)
        if normalized_query in path or (query_tokens & set(tokenize(path))):
            score += 1.0
        score += 0.5 * trigram_jaccard(query, f"{skill.name} {skill.description}")
        ranked.append((score, skill))
    ranked.sort(key=lambda item: (-item[0], item[1].name))
    return [
        {
            "name": skill.name,
            "path": str(skill.path),
            "version": skill.version,
            "description": skill.description,
            "score": round(score, 4),
        }
        for score, skill in ranked
    ]


def declared_dependencies(skill: Skill) -> list[str]:
    """All dependency names declared in the SKILL.md frontmatter (unfiltered)."""
    text = skill.path.joinpath("SKILL.md").read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text)
    declared: list[str] = []
    for key in ("requires", "dependencies"):
        for item in frontmatter.get(key, "").split(","):
            item = item.strip()
            if item and item not in declared:
                declared.append(item)
    return declared


def resolve_dependencies(skill: Skill, all_skills: list[Skill]) -> list[str]:
    """Declared dependencies that actually exist in ``all_skills`` (missing skipped)."""
    known = {candidate.name for candidate in all_skills}
    return [name for name in declared_dependencies(skill) if name in known]


def _workflow_steps(skill: Skill) -> list[str]:
    """Numbered list items from the SKILL.md `## Workflow` section."""
    text = skill.path.joinpath("SKILL.md").read_text(encoding="utf-8")
    steps: list[str] = []
    in_workflow = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_workflow = line.strip().lower() == "## workflow"
            continue
        if not in_workflow:
            continue
        match = _STEP_RE.match(line)
        if match:
            steps.append(match.group(1).strip())
    return steps


def compose(skill_names: list[str], all_skills: list[Skill]) -> dict:
    """Merge each named skill's workflow steps into a composed workflow."""
    by_name = {skill.name: skill for skill in all_skills}
    names: list[str] = []
    workflow: list[str] = []
    for name in skill_names:
        skill = by_name.get(name)
        if skill is None:
            continue
        names.append(skill.name)
        workflow.extend(_workflow_steps(skill))
    return {"composed": {"workflow": workflow}, "skills": names, "conflicts": []}


def verify(skill: Skill) -> dict:
    """Structural checks for a skill: frontmatter, name, description and tests."""
    checks = {
        "frontmatter": "name" in skill.frontmatter and "description" in skill.frontmatter,
        "name": skill.name == skill.path.name,
        "description": bool(skill.description),
        "tests": skill.has_tests,
    }
    errors: list[str] = []
    if not checks["frontmatter"]:
        errors.append("frontmatter is missing name or description")
    if not checks["name"]:
        errors.append("frontmatter name does not match directory name")
    if not checks["description"]:
        errors.append("description is empty")
    if not checks["tests"]:
        errors.append("missing tests/ directory")
    return {"name": skill.name, "valid": all(checks.values()), "checks": checks, "errors": errors}
