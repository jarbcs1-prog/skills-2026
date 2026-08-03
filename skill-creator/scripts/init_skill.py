"""Scaffold new skills from the ten template classes.

Usage (CLI): ``python scripts/init_skill.py <name> <template> [--description ...]
[--author ...] [--version ...] [--output DIR] [--dependencies a,b,c]``
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from scripts.templates import (
    TEMPLATES,
    placeholders_substitute,
    read_shared,
    template_file,
)

_NAME_RE = r"^[a-z0-9]+(-[a-z0-9]+)*$"

_SUBDIRS = ("scripts", "references", "assets", "tests", "evals")


class SkillNameError(ValueError):
    """Raised when a skill name is not valid kebab-case."""


def validate_name(name: str) -> str:
    """Validate that ``name`` is kebab-case, returning it unchanged."""
    if not name:
        raise SkillNameError("skill name must not be empty")
    if not __import__("re").match(_NAME_RE, name):
        raise SkillNameError(
            f"skill name {name!r} must be kebab-case (lowercase letters, digits, "
            "single hyphens between words)"
        )
    return name


@dataclass
class SkillMetadata:
    """Metadata written into a scaffolded skill.yaml manifest."""

    name: str
    description: str
    author: str = "unknown"
    version: str = "1.0.0"
    license: str = "MIT"
    dependencies: list[str] = field(default_factory=list)
    scripts: list[str] = field(
        default_factory=lambda: ["scripts/validate_skill.py"]
    )
    references: list[str] = field(default_factory=list)
    assets: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=lambda: ["tests/test_skill.py"])
    evals: list[str] = field(default_factory=lambda: ["evals/evals.json"])

    def to_yaml(self) -> str:
        """Render the manifest as YAML with JSON-encoded list values."""
        lines = [
            f"name: {self.name}",
            f"version: {self.version}",
            f"description: {self.description}",
            f"author: {self.author}",
            f"license: {self.license}",
            "compatibility:",
            '  opencode: ">=0.1.0"',
            "  platforms:",
            "    - windows",
            "    - macos",
            "    - linux",
            f"dependencies: {json.dumps(self.dependencies)}",
            f"scripts: {json.dumps(self.scripts)}",
            f"references: {json.dumps(self.references)}",
            f"assets: {json.dumps(self.assets)}",
            f"tests: {json.dumps(self.tests)}",
            f"evals: {json.dumps(self.evals)}",
        ]
        return "\n".join(lines) + "\n"


_VALIDATE_SKILL_SOURCE = (
    Path(__file__).resolve().parent / "validate_skill.py"
).read_text(encoding="utf-8")

_TEST_SKILL_TEMPLATE = """\"\"\"Smoke tests for a scaffolded skill.\"\"\"

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_skill_has_required_files():
    assert (ROOT / "SKILL.md").exists()
    assert (ROOT / "skill.yaml").exists()
    assert (ROOT / "evals" / "evals.json").exists()
"""


class SkillScaffolder:
    """Create a new skill directory from one of the ten templates."""

    def __init__(self) -> None:
        self.templates = TEMPLATES

    def create(
        self,
        name: str,
        template: str,
        target_dir: str | Path = ".",
        description: str = "",
        author: str = "unknown",
        version: str = "1.0.0",
        dependencies: list[str] | None = None,
    ) -> Path:
        """Scaffold ``name`` into ``target_dir``; returns the skill root."""
        validate_name(name)
        if template not in self.templates:
            raise ValueError(
                f"unknown template {template!r}; choose from "
                + ", ".join(self.templates)
            )

        root = Path(target_dir) / name
        if root.exists():
            raise FileExistsError(f"directory {root} already exists")

        if not description:
            description = self.templates[template]

        metadata = SkillMetadata(
            name=name,
            description=description,
            author=author,
            version=version,
            dependencies=list(dependencies or []),
        )
        mapping = {
            "name": name,
            "version": version,
            "description": description,
            "author": author,
            "dependencies": list(dependencies or []),
        }

        root.mkdir(parents=True, exist_ok=True)
        for subdir in _SUBDIRS:
            (root / subdir).mkdir(exist_ok=True)
        (root / ".github" / "workflows").mkdir(parents=True, exist_ok=True)

        skill_md_tpl = template_file(template, "SKILL.md.tpl").read_text(
            encoding="utf-8"
        )
        (root / "SKILL.md").write_text(
            placeholders_substitute(skill_md_tpl, mapping), encoding="utf-8"
        )

        evals_tpl = template_file(template, "evals.json.tpl").read_text(
            encoding="utf-8"
        )
        (root / "evals" / "evals.json").write_text(
            placeholders_substitute(evals_tpl, mapping), encoding="utf-8"
        )

        (root / "skill.yaml").write_text(metadata.to_yaml(), encoding="utf-8")

        (root / ".github" / "workflows" / "skill-test.yml").write_text(
            read_shared("workflow.yml.tpl"), encoding="utf-8"
        )

        (root / "scripts" / "__init__.py").write_text("", encoding="utf-8")
        (root / "scripts" / "validate_skill.py").write_text(
            _VALIDATE_SKILL_SOURCE, encoding="utf-8"
        )
        (root / "tests" / "__init__.py").write_text("", encoding="utf-8")
        (root / "tests" / "test_skill.py").write_text(
            _TEST_SKILL_TEMPLATE, encoding="utf-8"
        )
        (root / "references" / "README.md").write_text(
            "# References\n\nPut reference material for this skill here.\n",
            encoding="utf-8",
        )
        (root / "assets" / "README.md").write_text(
            "# Assets\n\nPut static assets (HTML reports, images) for this skill here.\n",
            encoding="utf-8",
        )
        return root


def list_scaffolded_files(skill_dir: str | Path) -> list[str]:
    """Return relative paths of every file created by the scaffolder."""
    root = Path(skill_dir)
    if not root.exists():
        return []
    return [
        str(path.relative_to(root))
        for path in sorted(root.rglob("*"))
        if path.is_file()
    ]


def main() -> None:
    parser = argparse.ArgumentParser(prog="skill-creator-init")
    parser.add_argument("name", help="skill name in kebab-case")
    parser.add_argument("template", choices=sorted(TEMPLATES))
    parser.add_argument("--description", default="")
    parser.add_argument("--author", default="unknown")
    parser.add_argument("--version", default="1.0.0")
    parser.add_argument("--output", default=".")
    parser.add_argument("--dependencies", default="", help="comma-separated")
    args = parser.parse_args()

    dependencies = [d.strip() for d in args.dependencies.split(",") if d.strip()]
    try:
        root = SkillScaffolder().create(
            args.name,
            args.template,
            target_dir=args.output,
            description=args.description,
            author=args.author,
            version=args.version,
            dependencies=dependencies,
        )
    except (SkillNameError, FileExistsError, ValueError) as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    print(f"Created skill at {root}")
    for file in list_scaffolded_files(root):
        print(f"  {file}")


if __name__ == "__main__":
    main()
