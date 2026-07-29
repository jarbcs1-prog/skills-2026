# AI Self-Reflection

A metacognitive improvement protocol for AI agents. Converts task experiences into validated process improvements through friction detection, reflection, generalization, and behavioral updates.

## What It Does

Every AI task produces two outputs:

1. **Task Output** — the user-facing result
2. **Process Output** — changes to how future tasks are approached

This skill captures the second output. It detects friction (where approach mismatched requirement), generalizes lessons, validates them through evidence, and promotes confirmed improvements into persistent capabilities.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/jarbcs1-prog/skills-2026.git
cd skills-2026/ai-improved-self-reflection

# Initialize memory storage
python main.py initialize

# Record a reflection event
python main.py record \
  --task "Refactored auth module" \
  --category "structure" \
  --observation "Used prose instead of bullet points for conceptual explanation" \
  --friction "format" \
  --root-cause "Chose familiar format before evaluating communication need" \
  --lesson "Choose representation after identifying information need" \
  --scope "explanations" \
  --confidence 0.78 \
  --action "Evaluate information type before choosing format"

# Generate candidate lessons from reflections
python main.py distill

# Generate a system report
python main.py report
```

## CLI Reference

| Command | Purpose |
|---------|---------|
| `initialize` | Create memory directory and default files |
| `record` | Record a reflection event |
| `distill` | Generate candidate lessons from reflection patterns |
| `promote` | Promote validated candidates to capabilities |
| `validate` | Record validation evidence for a capability |
| `report` | Generate a full system report (JSON) |
| `bridge` | Inject validated capabilities as runtime prompt overlay |
| `prune` | Cap memory file sizes by keeping most recent N records |

### record

```bash
python main.py record \
  --task "Task description" \
  --category "Category" \
  --observation "What happened" \
  --friction "Friction type" \
  --root-cause "Why it happened" \
  --lesson "Generalized lesson" \
  --scope "Scope of applicability" \
  --confidence 0.8 \
  --action "Future action"
```

Optional flags: `--evidence N`, `--audience "who"`, `--criteria "what"`, `--corrections N`, `--clarifications N`, `--reprompts N`

### validate

```bash
python main.py validate \
  --capability "Capability name" \
  --task "Task where validated" \
  --outcome "Result description" \
  --success \
  --delta 0.15
```

### report

```bash
python main.py report
```

Returns JSON with: reflection statistics, friction patterns, capability status, validation history, and capability health.

### bridge

```bash
python main.py bridge --scope general
```

Generates a compact `### OPERATIONAL CONSTRAINTS` prompt overlay from validated capabilities. Filters by scope, ranks by `validation_score × confidence`, and caps output at `TokenBudget` (default 500 tokens). Use this to inject learned behavioral constraints into an agent's system prompt at runtime.

### prune

```bash
python main.py prune --limit 500
```

Keeps only the most recent N records in `reflection_events.json` and `validation_history.json`. Prevents unbounded memory growth in long-running sessions.

## Project Structure

```
ai-improved-self-reflection/
├── SKILL.md              # Skill definition and metacognitive protocol
├── README.md             # This file
├── HOWTO.md              # Integration guide
├── LICENSE               # MIT License
├── main.py               # Entry point
├── models.py             # Core data models (dataclasses + enums)
├── storage.py            # JSON persistence layer
├── reflection.py         # Reflection event capture
├── distillation.py       # Pattern detection and candidate generation
├── capability.py         # Capability promotion layer
├── validation.py         # Capability validation
├── analysis.py           # System analysis and reporting
├── bridge.py             # Runtime bridge: capability-to-prompt injection
├── cli.py                # Command-line interface
├── memory/               # Runtime data (gitignored)
│   ├── friction_log.md   # Human-readable reflection log
│   ├── reflection_events.json
│   ├── candidate_lessons.json
│   ├── capabilities_memory.json
│   └── validation_history.json
└── tests/                # 53 tests across 8 modules
```

## How It Works

The reflection lifecycle has 5 stages:

1. **Observation** — Detect friction between approach and requirement
2. **Diagnosis** — Identify root cause of the mismatch
3. **Generalization** — Extract transferable lesson from the specific event
4. **Validation** — Gather evidence across multiple contexts
5. **Capability Update** — Promote validated lessons to persistent behaviors

Lessons require minimum evidence (2+ occurrences) and confidence thresholds before promotion:

- **GLOBAL** level: 5+ evidence, confidence >= 0.75
- **LOCAL** level: 3+ evidence, confidence >= 0.55

## Testing

```bash
python -m pytest tests/ -v
```

42 tests across models, storage, reflection, distillation, capability, validation, and analysis modules.

## Runtime Bridge

The `bridge` command provides capability-to-prompt injection — the most advanced feature of this skill. It queries validated capabilities, ranks them by quality, and generates a compact overlay that can be injected into any agent's system prompt.

```python
from bridge import RuntimeReflectionBridge, TokenBudget

bridge = RuntimeReflectionBridge(TokenBudget(max_capability_tokens=500))
overlay = bridge.build_system_prompt_overlay(scope="general")
print(overlay)
```

## Model Agnostic

This skill works with any LLM. The SKILL.md protocol is designed to be loaded as context by any AI agent. The CLI tools are Python-based and model-independent.

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `python -m pytest tests/ -v`
5. Submit a pull request
