#!/usr/bin/env python3
"""
Scaffold a new skill directory with the standard structure.

Creates:
- SKILL.md from the SKILL.md template
- scripts/ directory with an __init__.py and example script
- references/ directory with a placeholder
- templates/ directory with a placeholder

Usage:
    python init_skill.py <skill-name>
    python init_skill.py my-cool-skill --target-dir ./skills

Returns exit code 0 on success, 1 on error.
"""

import argparse
import os
import sys
from pathlib import Path


SKILL_MD_CONTENT = """\
---
name: {name}
description: |
  {description}
---

# {title}

{description}

## When to Trigger

1. {trigger_1}
2. {trigger_2}

## Workflow

### Step 1: {step_name}

{step_description}

## References

- `references/overview.md` — Overview documentation for this skill

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/example.py` | Example helper script |
"""

SCRIPT_EXAMPLE = """\
#!/usr/bin/env python3
\"\"\"
Example helper script for {name}.
\"\"\"
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Example script for {name}")
    args = parser.parse_args()
    print("Hello from {name}!")


if __name__ == "__main__":
    main()
"""

REFERENCES_PLACEHOLDER = """\
# {title} — Overview

Add detailed reference documentation here.
"""

TEMPLATES_PLACEHOLDER = """\
# Templates

Add reusable templates, boilerplate files, or sample data here.
"""

INIT_PY = ""


def create_skill_directory(target: Path, name: str) -> None:
    """Create the full skill directory structure."""
    target.mkdir(parents=True, exist_ok=True)

    # SKILL.md
    skill_md = target / "SKILL.md"
    title = name.replace("-", " ").replace("_", " ").title()
    skill_md.write_text(
        SKILL_MD_CONTENT.format(
            name=name,
            title=title,
            description=f"A skill for {title.lower()} functionality.",
            trigger_1="User requests a task related to this skill",
            trigger_2="User mentions relevant keywords",
            step_name="First Step",
            step_description="Describe the first step of the workflow here.",
        ),
        encoding="utf-8",
    )
    print(f"  Created {skill_md.relative_to(target.parent)}")

    # scripts/
    scripts_dir = target / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    (scripts_dir / "__init__.py").write_text(INIT_PY, encoding="utf-8")

    example_script = scripts_dir / "example.py"
    example_script.write_text(
        SCRIPT_EXAMPLE.format(name=name),
        encoding="utf-8",
    )
    print(f"  Created {scripts_dir.relative_to(target.parent)}/")

    # references/
    refs_dir = target / "references"
    refs_dir.mkdir(exist_ok=True)
    (refs_dir / "overview.md").write_text(
        REFERENCES_PLACEHOLDER.format(title=title),
        encoding="utf-8",
    )
    print(f"  Created {refs_dir.relative_to(target.parent)}/")

    # templates/
    tmpl_dir = target / "templates"
    tmpl_dir.mkdir(exist_ok=True)
    (tmpl_dir / "README.md").write_text(
        TEMPLATES_PLACEHOLDER.format(title=title),
        encoding="utf-8",
    )
    print(f"  Created {tmpl_dir.relative_to(target.parent)}/")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a new skill directory with the standard structure."
    )
    parser.add_argument(
        "skill_name",
        help="Name of the skill (lowercase, hyphens allowed, e.g. my-cool-skill)",
    )
    parser.add_argument(
        "--target-dir",
        default=".",
        help="Parent directory where the skill folder will be created (default: current directory)",
    )
    args = parser.parse_args()

    name = args.skill_name.strip().lower().replace(" ", "-")
    if not name.isidentifier() and not all(c.isalnum() or c == "-" for c in name):
        print(
            f"Error: Skill name '{name}' contains invalid characters. Use lowercase letters, digits and hyphens.",
            file=sys.stderr,
        )
        return 1

    target = Path(args.target_dir).resolve() / name

    if target.exists():
        print(f"Error: Directory '{target}' already exists", file=sys.stderr)
        return 1

    print(f"Creating skill: {name}")
    create_skill_directory(target, name)
    print(f"\nDone! Skill created at: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
