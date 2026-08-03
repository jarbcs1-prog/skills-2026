#!/usr/bin/env python3
"""Skill structure validation for the writing-skills skill.

Validates a skill directory against the writing-skills conventions:
frontmatter rules (name kebab-case, description "Use when...", max length),
required files, referenced directories and the optional skill.yaml manifest.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .scaffolder import _NAME_RE

_MAX_FRONTMATTER = 1024
_MAX_DESCRIPTION = 500


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    score: int = 100

    def summary(self) -> str:
        status = "VALID" if self.valid else "INVALID"
        return f"{status} (score {self.score}/100, {len(self.errors)} errors, {len(self.warnings)} warnings)"


class SkillValidator:
    """Validates skill directories against writing-skills conventions."""

    def validate(self, skill_path: Path, strict: bool = False) -> ValidationResult:
        skill_path = Path(skill_path)
        errors: list[str] = []
        warnings: list[str] = []

        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            errors.append("SKILL.md missing - every skill needs a SKILL.md")
            return ValidationResult(False, errors, warnings, 0)

        text = skill_md.read_text(encoding="utf-8")
        frontmatter = self._parse_frontmatter(text)
        self._validate_frontmatter(frontmatter, errors, warnings)

        for directory in ("scripts", "references", "assets", "evals"):
            if (skill_path / directory).exists():
                for ref in self._references_to(directory, skill_md):
                    if not (skill_path / directory / ref).exists():
                        errors.append(
                            f"Reference in SKILL.md points to missing file: {directory}/{ref}"
                        )

        manifest = skill_path / "skill.yaml"
        if manifest.exists():
            manifest_text = manifest.read_text(encoding="utf-8")
            if "name:" not in manifest_text or "version:" not in manifest_text:
                warnings.append("skill.yaml exists but lacks name/version fields")

        evals = skill_path / "evals" / "evals.json"
        if evals.exists():
            if '{"skill_name"' not in evals.read_text(encoding="utf-8").replace(" ", "").replace("\n", "") \
               and '"skill_name"' not in evals.read_text(encoding="utf-8"):
                warnings.append("evals/evals.json does not declare skill_name")

        if not (skill_path / "scripts").exists() and not (skill_path / "references").exists():
            warnings.append("skill has no scripts/ or references/ dirs (fine for self-contained skills)")

        if len(text.split()) < 20:
            warnings.append("SKILL.md is very short (< 20 words); may lack real guidance")

        score = max(0, 100 - 5 * len(errors) - len(warnings))
        valid = not errors
        if strict and score < 70:
            valid = False
        return ValidationResult(valid, errors, warnings, score)

    @staticmethod
    def _parse_frontmatter(text: str) -> dict[str, str]:
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
        if not match:
            return {}
        data: dict[str, str] = {}
        for line in match.group(1).splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                data[key.strip()] = value.strip()
        return data

    @staticmethod
    def _references_to(directory: str, skill_md: Path) -> list[str]:
        text = skill_md.read_text(encoding="utf-8")
        return re.findall(rf"{directory}/([\w./\-]+)", text)

    @staticmethod
    def _validate_frontmatter(
        frontmatter: dict[str, str], errors: list[str], warnings: list[str]
    ) -> None:
        name = frontmatter.get("name", "")
        if not name:
            errors.append("frontmatter missing 'name' field")
        elif not _NAME_RE.match(name):
            errors.append(
                f"frontmatter name {name!r} invalid: use lowercase letters, numbers, hyphens only"
            )

        description = frontmatter.get("description", "")
        if not description:
            errors.append("frontmatter missing 'description' field")
        else:
            if not description.startswith("Use when"):
                warnings.append("description should start with 'Use when...' (triggering conditions)")
            if description == description.lower() or not any(
                c.isupper() for c in description[:1]
            ):
                pass  # third-person is fine lowercase; do not over-flag
            if "flowchart" in description.lower() or "step" in description.lower():
                warnings.append(
                    "description may summarize the workflow; descriptions should only state WHEN to use"
                )

        joined = "name: " + name + "\n" + "description: " + description
        if len(joined) > _MAX_FRONTMATTER:
            errors.append(f"frontmatter exceeds {_MAX_FRONTMATTER} chars")
        if len(description) > _MAX_DESCRIPTION:
            warnings.append(f"description exceeds {_MAX_DESCRIPTION} chars; keep it short")
