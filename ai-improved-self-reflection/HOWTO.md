# HOWTO — Integration Guide

Practical instructions for installing and using the AI Self-Reflection skill across different environments.

---

## Table of Contents

1. [Installation](#installation)
2. [Standalone CLI Usage](#standalone-cli-usage)
3. [OpenCode CLI](#opencode-cli)
4. [OpenCode Desktop](#opencode-desktop)
5. [Hermes Agent](#hermes-agent)
6. [OpenClaw / Claude Code / Codex](#openclaw--claude-code--codex)
7. [Python Library](#python-library)
8. [Custom Integration](#custom-integration)

---

## Installation

### Requirements

- Python 3.10 or later
- No external dependencies (stdlib only)

### Windows

```powershell
git clone https://github.com/jarbcs1-prog/skills-2026.git
cd skills-2026\ai-improved-self-reflection
python main.py initialize
```

### Linux

```bash
git clone https://github.com/jarbcs1-prog/skills-2026.git
cd skills-2026/ai-improved-self-reflection
python3 main.py initialize
```

### macOS

```bash
git clone https://github.com/jarbcs1-prog/skills-2026.git
cd skills-2026/ai-improved-self-reflection
python3 main.py initialize
```

All platforms use the same codebase. No platform-specific setup required.

### Verify Installation

```bash
python main.py --help
python -m pytest tests/ -v
```

You should see the CLI help and 53 passing tests.

---

## Standalone CLI Usage

The simplest way to use the skill. Run commands directly from the project directory.

### Record a Reflection

```bash
python main.py record \
  --task "Built REST API endpoint" \
  --category "epistemic" \
  --observation "Over-explained simple endpoint to experienced developer" \
  --friction "conceptual" \
  --root-cause "Defaulted to verbose explanation without assessing audience" \
  --lesson "Match explanation depth to audience expertise" \
  --scope "technical communication" \
  --confidence 0.85 \
  --action "Check audience context before choosing detail level"
```

### Distill Lessons

```bash
python main.py distill
```

Scans reflection events, groups by lesson, and generates candidate lessons when patterns emerge (2+ evidence).

### Promote Capabilities

```bash
python main.py promote
```

Promotes validated candidates to persistent capabilities based on evidence and confidence thresholds.

### Validate a Capability

```bash
python main.py validate \
  --capability "Audience Matching" \
  --task "Explained microservices to junior dev" \
  --outcome "Used concrete examples, developer understood immediately" \
  --success \
  --delta 0.12
```

### Generate Report

```bash
python main.py report
```

Returns a JSON report covering reflection statistics, friction patterns, capability status, validation history, and health metrics.

### Inject Capabilities at Runtime (Bridge)

```bash
python main.py bridge --scope general
```

Generates a `### OPERATIONAL CONSTRAINTS` prompt overlay from validated capabilities. The overlay is filtered by scope, ranked by `validation_score × confidence`, and capped at `TokenBudget` (default 500 tokens).

Use this to dynamically inject learned behavioral constraints into an agent's system prompt. The bridge queries `capabilities_memory.json` and outputs only active, validated capabilities.

```bash
# Filter by specific scope
python main.py bridge --scope cli
```

### Prune Memory Files

```bash
python main.py prune --limit 500
```

Keeps only the most recent N records in `reflection_events.json` and `validation_history.json`. Prevents unbounded memory growth in long-running agent sessions.

---

## OpenCode CLI

### Method 1: Copy SKILL.md

Copy `SKILL.md` into your OpenCode skills directory:

```bash
# Linux/macOS
cp SKILL.md ~/.opencode/skills/ai-self-reflection.md

# Windows
copy SKILL.md %USERPROFILE%\.opencode\skills\ai-self-reflection.md
```

### Method 2: Reference the Repository

Add the repo path to your OpenCode configuration:

```json
{
  "skills": [
    {
      "name": "ai-self-reflection",
      "path": "F:\\skills_2026\\ai-improved-self-reflection\\SKILL.md"
    }
  ]
}
```

### Method 3: Use the CLI Tools

From any OpenCode session, run the CLI tools directly:

```bash
cd /path/to/ai-improved-self-reflection
python main.py record --task "..." --category "..."
```

---

## OpenCode Desktop

Same as OpenCode CLI. Copy `SKILL.md` to the skills directory, or reference the repository path in your configuration.

For the Desktop GUI, the skill protocol loads as system context. The CLI tools can be run from an integrated terminal.

---

## Hermes Agent

Hermes Agent loads skills from its skill directory.

```bash
# Copy SKILL.md to Hermes skills directory
cp SKILL.md /path/to/hermes/skills/ai-self-reflection.md
```

Hermes will automatically load the skill when the task matches the description triggers (friction detection, repeated failure patterns, process improvement).

For CLI access, Hermes can shell out to the Python tools:

```bash
cd /path/to/ai-improved-self-reflection
python main.py record --task "..." --category "..."
```

---

## OpenClaw / Claude Code / Codex

These agents support loading SKILL.md as context.

### Claude Code

Copy `SKILL.md` into the Claude Code skills directory:

```bash
# Linux/macOS
cp SKILL.md ~/.claude/skills/ai-self-reflection.md

# Windows
copy SKILL.md %USERPROFILE%\.claude\skills\ai-self-reflection.md
```

### OpenClaw

Add the skill path to your OpenClaw configuration:

```json
{
  "skills": ["path/to/ai-improved-self-reflection/SKILL.md"]
}
```

### Codex

```bash
cp SKILL.md ~/.codex/skills/ai-self-reflection.md
```

All three agents can also call the CLI tools via shell commands when they need to persist reflection data.

---

## Python Library

Import the modules directly in your agent code:

```python
from models import ReflectionEvent, FrictionType
from reflection import create_reflection, classify_friction
from distillation import distill_candidates
from capability import promote_candidates
from validation import record_validation
from analysis import generate_system_report

# Create a reflection event
event = create_reflection(
    task="Built data pipeline",
    category="structure",
    observation="Used sequential approach for parallelizable task",
    friction="process",
    root_cause="Didn't evaluate task parallelism",
    lesson="Assess parallelism before choosing execution strategy",
    scope="data engineering",
    confidence=0.82,
    action="Check parallelism opportunities first"
)

# Distill candidates from reflections
candidates = distill_candidates()

# Generate a report
report = generate_system_report()
print(report)

# Generate a runtime prompt overlay from validated capabilities
from bridge import RuntimeReflectionBridge, TokenBudget

bridge = RuntimeReflectionBridge(TokenBudget(max_capability_tokens=500))
overlay = bridge.build_system_prompt_overlay(scope="general")
print(overlay)
```

---

## Custom Integration

### Storage Format

All data is stored as JSON in the `memory/` directory:

- `reflection_events.json` — Array of reflection event objects
- `candidate_lessons.json` — Array of distilled candidate lessons
- `capabilities_memory.json` — Object with `capabilities`, `candidate_lessons`, `deprecated_patterns`
- `validation_history.json` — Array of validation records
- `friction_log.md` — Human-readable reflection log

### Reading Data

```python
from storage import load_json, REFLECTION_MEMORY, CAPABILITY_MEMORY

reflections = load_json(REFLECTION_MEMORY, [])
capabilities = load_json(CAPABILITY_MEMORY, {"capabilities": [], "candidate_lessons": [], "deprecated_patterns": []})
```

### Writing Data

```python
from storage import append_json_record, save_json, REFLECTION_MEMORY

append_json_record(REFLECTION_MEMORY, {
    "task": "My task",
    "category": "My category",
    "observation": "What happened",
    "friction": "Friction type",
    "root_cause": "Why",
    "lesson": "Generalized lesson",
    "scope": "Applicability scope",
    "confidence": 0.8,
    "evidence_count": 1,
    "action": "Future action",
    "communication": {
        "audience_assumptions": [],
        "hidden_criteria": [],
        "corrections": 0,
        "clarifications": 0,
        "re_prompts": 0
    }
})
```

### Webhook / Event-Driven

Trigger reflection recording from any event source:

```python
from reflection import create_reflection

def on_task_complete(task_result):
    if task_result.had_friction:
        create_reflection(
            task=task_result.task,
            category=task_result.friction_type,
            observation=task_result.observation,
            friction=task_result.friction,
            root_cause=task_result.root_cause,
            lesson=task_result.lesson,
            scope=task_result.scope,
            confidence=task_result.confidence,
            action=task_result.future_action
        )
```

---

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific module tests
python -m pytest tests/test_models.py -v
python -m pytest tests/test_storage.py -v
python -m pytest tests/test_reflection.py -v
python -m pytest tests/test_distillation.py -v
python -m pytest tests/test_capability.py -v
python -m pytest tests/test_validation.py -v
python -m pytest tests/test_analysis.py -v
python -m pytest tests/test_bridge.py -v
```

53 tests total across 8 modules.
