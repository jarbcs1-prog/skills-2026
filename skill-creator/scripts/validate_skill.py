"""Standalone skill validator for scaffolded skills.

Self-contained (stdlib only) so it can be copied verbatim into any
scaffolded skill and run there as ``python scripts/validate_skill.py .``.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


@dataclass
class ValidationResult:
    """Outcome of a skill validation pass."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    score: int = 100

    def summary(self) -> str:
        """Return a human-readable one-line verdict."""
        if self.valid:
            return f"VALID (score {self.score}/100)"
        return f"INVALID (score {self.score}/100): {len(self.errors)} error(s)"

    def render(self) -> str:
        """Return the full multi-line validation report."""
        lines = [self.summary()]
        for error in self.errors:
            lines.append(f"  ERROR: {error}")
        for warning in self.warnings:
            lines.append(f"  WARNING: {warning}")
        return "\n".join(lines)


def _parse_frontmatter(text: str) -> dict[str, str]:
    match = _FRONTMATTER_RE.search(text)
    if not match:
        return {}
    frontmatter: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip()
    return frontmatter


def validate_skill(skill_path: str | Path) -> ValidationResult:
    """Validate a skill directory against the scaffolded convention."""
    root = Path(skill_path)
    errors: list[str] = []
    warnings: list[str] = []

    skill_md = root / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md is missing")
        return ValidationResult(valid=False, errors=errors)

    text = skill_md.read_text(encoding="utf-8")
    frontmatter = _parse_frontmatter(text)
    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")

    if not name:
        errors.append("SKILL.md frontmatter is missing 'name'")
    elif not _NAME_RE.match(name):
        errors.append(
            f"SKILL.md name {name!r} is not kebab-case (a-z0-9 and single hyphens)"
        )
    if not description:
        errors.append("SKILL.md frontmatter is missing 'description'")
    elif len(description) > 1024:
        errors.append("SKILL.md description exceeds 1024 characters")

    manifest = root / "skill.yaml"
    manifest_name = ""
    if not manifest.exists():
        errors.append("skill.yaml is missing")
    else:
        manifest_text = manifest.read_text(encoding="utf-8")
        for line in manifest_text.splitlines():
            key, sep, value = line.partition(":")
            if sep and key.strip() == "name":
                manifest_name = value.strip()
        if not manifest_name:
            errors.append("skill.yaml is missing a 'name'")
        elif manifest_name != name:
            warnings.append(
                f"skill.yaml name {manifest_name!r} differs from SKILL.md name {name!r}"
            )

    for directory in ("scripts", "references", "assets", "tests", "evals"):
        if not (root / directory).exists():
            warnings.append(f"recommended directory {directory}/ is missing")

    evals_file = root / "evals" / "evals.json"
    if evals_file.exists():
        try:
            data = json.loads(evals_file.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "evals" not in data:
                warnings.append("evals/evals.json has no 'evals' key")
        except json.JSONDecodeError as exc:
            errors.append(f"evals/evals.json is not valid JSON: {exc}")

    for directory in ("scripts", "references", "assets", "tests"):
        pattern = re.compile(rf"{re.escape(directory)}/([\w./\-]+)")
        for reference in pattern.findall(text):
            if not (root / directory / reference).exists():
                errors.append(
                    f"SKILL.md references {directory}/{reference} which does not exist"
                )

    score = max(0, 100 - 5 * len(errors) - len(warnings))
    return ValidationResult(
        valid=not errors, errors=errors, warnings=warnings, score=score
    )


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: python scripts/validate_skill.py <skill_dir>")
        sys.exit(1)
    result = validate_skill(sys.argv[1])
    print(result.render())
    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
