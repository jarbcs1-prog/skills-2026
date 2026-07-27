# Collaborative Skill Engineering

A structured workflow for AI agents to collaboratively define, develop and validate new skills with users.

## Overview

This skill provides a step-by-step process for creating skills:

1. **Gather Requirements** — Understand the user's goal through targeted questions
2. **Plan Structure** — Identify scripts, references and templates needed
3. **Initialize** — Scaffold the skill directory with `init_skill.py`
4. **Develop** — Write SKILL.md content and resource files with iterative feedback
5. **Validate** — Check structure and content with `validate_skill.py`
6. **Deliver** — Present the finished skill

## Usage

### Scaffold a new skill

```bash
python scripts/init_skill.py my-new-skill
python scripts/init_skill.py my-new-skill --target-dir ./skills
```

This creates:

```
my-new-skill/
├── SKILL.md
├── scripts/
│   ├── __init__.py
│   └── example.py
├── references/
│   └── overview.md
└── templates/
    └── README.md
```

### Validate a skill

```bash
python scripts/validate_skill.py my-new-skill
```

Exit codes:
- `0` — Skill is valid (warnings may still appear)
- `1` — Validation errors found

Example output:

```
  WARN  references/ directory is empty
  WARN  No 'Trigger' or 'Workflow' section found
```

## Directory Structure

```
collaborative-skill-engineering/
├── SKILL.md                          # Main skill definition
├── README.md                         # This file
├── scripts/
│   ├── __init__.py
│   ├── init_skill.py                 # Scaffold a new skill
│   └── validate_skill.py             # Validate skill structure
├── references/
│   └── skill_structure_guide.md      # Skill anatomy and conventions
└── templates/
    ├── SKILL.md.template             # SKILL.md boilerplate
    └── scripts/
        └── example.py.template       # Script boilerplate
```

## References

- `references/skill_structure_guide.md` — Full guide to skill directory structure, frontmatter format, progressive disclosure and naming conventions.
