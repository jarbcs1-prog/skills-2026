# Skill Directory Structure Guide

This document describes the anatomy of a well-structured skill directory, the conventions for each component and how progressive disclosure keeps skills readable and maintainable.

---

## Directory Layout

```
my-skill/
├── SKILL.md              # Required — main entry point
├── scripts/              # Optional — executable helpers
│   ├── __init__.py
│   └── do_something.py
├── references/           # Optional — documentation loaded on demand
│   └── api_guide.md
└── templates/            # Optional — boilerplate files used in output
    └── output_template.md
```

### Required Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Main skill definition. Contains YAML frontmatter and markdown instructions. |

### Optional Directories

| Directory | Purpose | Loaded into context? |
|-----------|---------|----------------------|
| `scripts/` | Executable Python scripts, shell scripts, or utilities | No — invoked via shell |
| `references/` | Domain knowledge, API docs, detailed guides | Only when agent reads a specific file |
| `templates/` | Boilerplate templates, sample data, starter files | Only when agent reads a specific file |

---

## SKILL.md Frontmatter

Every `SKILL.md` must begin with a YAML frontmatter block delimited by `---`.

```yaml
---
name: my-skill
description: |
  One or two sentences describing what this skill does and when
  an agent should activate it. Be specific about trigger conditions.
---
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique skill identifier (lowercase, hyphens allowed) |
| `description` | string | Activation description — what triggers this skill and why |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Semantic version (e.g. `1.0.0`) |
| `author` | string | Skill author name or handle |
| `tags` | list | Searchable tags for skill discovery |

---

## SKILL.md Body Sections

After the frontmatter, the body uses standard Markdown. The following sections are recommended:

### 1. Title (`# Skill Name`)

A single H1 heading matching the skill name.

### 2. When to Trigger

A numbered list or paragraph describing the exact conditions under which the agent should activate this skill. Clear trigger rules prevent false activations.

**Good pattern:**
```markdown
## When to Trigger

1. User asks to create a new skill or update an existing one
2. User mentions "skill-creator", "SKILL.md", or "skill scaffolding"
3. User provides a skill directory path and asks for validation
```

**Bad pattern:**
```markdown
## When to Trigger
When appropriate.
```

### 3. Workflow

Step-by-step instructions for the agent. Each step should have:
- A clear heading (`### Step N: Name`)
- A description of what to do
- The agent action to take (e.g. which tool to use)

### 4. References

A bullet list pointing to files in `references/` with one-line descriptions:

```markdown
## References

- `references/api_guide.md` — API endpoint documentation
- `references/examples.md` — Worked examples for common cases
```

### 5. Scripts

A table of available scripts with their purpose:

```markdown
## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/validate.py` | Validates skill directory structure |
| `scripts/init.py` | Scaffolds a new skill directory |
```

---

## Progressive Disclosure Levels

Skills should follow a three-level disclosure model to keep context usage efficient:

### Level 1 — Metadata (always loaded)

- **Where:** SKILL.md frontmatter (`name`, `description`)
- **Cost:** ~50–100 tokens
- **Purpose:** Enables the orchestrator to decide whether to load the skill

### Level 2 — Instructions (loaded when skill is activated)

- **Where:** SKILL.md body
- **Cost:** ~200–1000 tokens
- **Purpose:** Core workflow steps the agent follows

### Level 3 — Resources (loaded on demand)

- **Where:** `references/`, `templates/`, `scripts/`
- **Cost:** Variable
- **Purpose:** Deep-dive documentation, example data, executable tools

### Example Progressive Disclosure

```
Level 1 (always):   name: "pdf-editor"
                     description: "Edit, merge, split PDF files..."

Level 2 (on load):  ## Workflow
                     ### Step 1: Identify the operation
                     ### Step 2: Run the appropriate script
                     ...
                     ## Scripts
                     | Script | Purpose |
                     | merge.py | Merge multiple PDFs |

Level 3 (on demand): references/merge_guide.md — detailed merge options
                      templates/cover_page.html — boilerplate cover page
```

---

## Good vs Bad Patterns

### Good SKILL.md Patterns

```markdown
---
name: data-cleaner
description: |
  Clean messy CSV/JSON data files. Use when the user has dirty
  tabular data with missing values, inconsistent formatting, or
  duplicate rows.
---

# Data Cleaner

## When to Trigger

1. User provides a CSV or JSON file with messy data
2. User asks to "clean", "fix", or "normalize" a dataset
3. User mentions duplicate removal, type coercion, or imputation

## Workflow

### Step 1: Inspect the Data

Run the validation script to identify issues:
\`\`\`bash
python scripts/validate_data.py <file_path>
\`\`\`

### Step 2: Apply Cleaning Rules

Based on the validation report, apply fixes using the clean script:
\`\`\`bash
python scripts/clean_data.py <file_path> --output cleaned_<file>
\`\`\`

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/validate_data.py` | Scan and report data quality issues |
| `scripts/clean_data.py` | Apply cleaning transformations |

## References

- `references/cleaning_rules.md` — Full list of cleaning rules and options
```

### Bad SKILL.md Patterns

```markdown
---
name: helper
description: Helps with stuff
---

# Helper

Do things with files. Use scripts when needed.
```

**Problems:**
- Description is vague — no trigger conditions
- No workflow steps
- No references to scripts or documentation
- Agent has no guidance on what to do

---

## Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| Skill directory | lowercase, hyphens | `my-cool-skill/` |
| SKILL.md field `name` | matches directory name | `my-cool-skill` |
| Scripts | snake_case, `.py` extension | `scripts/fetch_data.py` |
| References | snake_case, `.md` extension | `references/api_guide.md` |
| Templates | descriptive names | `templates/report.md` |

---

## Validation Rules

A skill is considered **valid** when:

1. `SKILL.md` exists in the root
2. Frontmatter contains both `name` and `description`
3. Body contains at least one H1 heading
4. All `.py` files in `scripts/` have valid syntax
5. No critical structural issues

Run `python scripts/validate_skill.py <skill_dir>` to check automatically.
