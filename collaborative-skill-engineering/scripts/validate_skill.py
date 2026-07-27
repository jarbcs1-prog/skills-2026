#!/usr/bin/env python3
"""
Validate a skill directory structure and SKILL.md content.

Checks:
- SKILL.md exists and has valid YAML frontmatter (name + description)
- Required sections present in SKILL.md body
- Expected directories (scripts/, references/, templates/) exist
- Scripts are syntactically valid Python

Usage:
    python validate_skill.py <skill_directory>

Returns exit code 0 if valid, 1 if errors found.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import NamedTuple

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


class Issue(NamedTuple):
    level: str  # "error" or "warning"
    message: str


def parse_frontmatter(content: str) -> tuple[dict | None, str | None]:
    """Extract YAML frontmatter and body from a SKILL.md file.

    Returns (frontmatter_dict, body) or (None, error_string).
    """
    if not content.startswith("---"):
        return None, "File does not start with --- (no frontmatter block)"

    # Find the closing ---
    second_dash = content.find("---", 3)
    if second_dash == -1:
        return None, "Unclosed frontmatter block (no closing ---)"

    raw_yaml = content[3:second_dash].strip()
    body = content[second_dash + 3:].strip()

    if yaml is not None:
        try:
            data = yaml.safe_load(raw_yaml)
            if not isinstance(data, dict):
                return None, "Frontmatter is not a YAML mapping"
            return data, body
        except yaml.YAMLError as exc:
            return None, f"YAML parse error: {exc}"
    else:
        # Fallback: simple regex-based extraction without PyYAML
        data: dict[str, str] = {}
        for line in raw_yaml.splitlines():
            line = line.strip()
            m = re.match(r"^(\w[\w-]*):\s*(.*)", line)
            if m:
                data[m.group(1)] = m.group(2).strip()
        return data, body


def find_sections(body: str) -> list[str]:
    """Return a list of H2/H3 section headings found in the body."""
    return re.findall(r"^#{2,3}\s+(.+)", body, re.MULTILINE)


def check_python_syntax(filepath: Path) -> str | None:
    """Compile-check a Python file. Returns error message or None."""
    try:
        compile(filepath.read_text(encoding="utf-8"), str(filepath), "exec")
        return None
    except SyntaxError as exc:
        return f"Syntax error: {exc.msg} (line {exc.lineno})"


def validate_skill_directory(skill_dir: Path) -> list[Issue]:
    """Run all validation checks against a skill directory."""
    issues: list[Issue] = []

    # --- SKILL.md existence ---
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        issues.append(Issue("error", "SKILL.md not found"))
        return issues  # Can't proceed without it

    # --- Frontmatter ---
    raw = skill_md.read_text(encoding="utf-8")
    frontmatter, body_or_err = parse_frontmatter(raw)

    if frontmatter is None:
        issues.append(Issue("error", f"Invalid frontmatter: {body_or_err}"))
        return issues

    if "name" not in frontmatter or not frontmatter["name"]:
        issues.append(Issue("error", "Frontmatter missing required field: name"))

    if "description" not in frontmatter or not frontmatter["description"]:
        issues.append(Issue("error", "Frontmatter missing required field: description"))

    # --- Required sections ---
    body = body_or_err or ""
    sections = find_sections(body)
    section_lower = {s.lower() for s in sections}

    # At least one H1 heading
    h1_matches = re.findall(r"^#\s+(.+)", body, re.MULTILINE)
    if not h1_matches:
        issues.append(Issue("error", "SKILL.md body has no H1 heading (# Title)"))

    # Warn on missing common sections
    expected_keywords = {"trigger", "workflow", "step"}
    has_any_trigger = any(kw in s for s in section_lower for kw in expected_keywords)
    if not has_any_trigger:
        issues.append(Issue("warning", "No 'Trigger' or 'Workflow' section found — consider adding one"))

    # --- Directory checks ---
    for dirname in ("scripts", "references", "templates"):
        dirpath = skill_dir / dirname
        if dirpath.is_dir():
            if not any(dirpath.iterdir()):
                issues.append(Issue("warning", f"{dirname}/ directory is empty"))
        else:
            issues.append(Issue("warning", f"{dirname}/ directory missing (optional but recommended)"))

    # --- Python syntax check ---
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        for py_file in scripts_dir.glob("*.py"):
            err = check_python_syntax(py_file)
            if err:
                issues.append(Issue("error", f"scripts/{py_file.name}: {err}"))

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a skill directory structure and SKILL.md content."
    )
    parser.add_argument(
        "skill_directory",
        help="Path to the skill directory to validate",
    )
    args = parser.parse_args()

    skill_dir = Path(args.skill_directory).resolve()
    if not skill_dir.is_dir():
        print(f"Error: '{skill_dir}' is not a directory", file=sys.stderr)
        return 1

    issues = validate_skill_directory(skill_dir)

    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]

    if not issues:
        print(f"OK Skill directory is valid: {skill_dir.name}")
        return 0

    for issue in warnings:
        print(f"  WARN  {issue.message}")
    for issue in errors:
        print(f"  ERROR {issue.message}", file=sys.stderr)

    if errors:
        print(f"\nValidation failed with {len(errors)} error(s) and {len(warnings)} warning(s)", file=sys.stderr)
        return 1
    else:
        print(f"\nValidation passed with {len(warnings)} warning(s)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
