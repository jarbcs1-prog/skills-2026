# Skills 2026

A collection of 42 AI agent skills for LLM routing, context management, self-reflection, collaborative skill engineering, and more.

## Authorship & Attribution

I created the following skills from scratch or rebuilt them substantially: **ai-self-reflection**, **collaborative-skill-engineering**, **chinese-translator**, **dynamic-context-pruning** (this version), and **opencode-zen-delegator**.

All other skills in this repository are pre-existing work by their respective creators and contributors, refactored here to improve efficiency, performance, and model-agnostic compatibility. I am deeply grateful to the original authors and all contributors who built and maintained these skills. This repository is a collaborative effort, and credit belongs entirely to those who originated and shaped each skill.

## Skills Overview

| Skill | Description | Status |
|-------|-------------|--------|
| [ai-self-reflection](#ai-self-reflection) | Metacognitive improvement protocol — friction detection, reflection, distillation and validated capability promotion | Production-Ready |
| [brainstorming](#brainstorming) | Idea exploration with design-doc validation, spec diffing, and decision matrices | Production-Ready |
| [code-quality](#code-quality) | Pre-commit quality gates with config, incremental mode, and IDE integration | Production-Ready |
| [code-reviewer](#code-reviewer) | Rule engine with 38 regex rules, SARIF output, CI gate, and review history | Production-Ready |
| [collaborative-skill-engineering](#collaborative-skill-engineering) | Interactive workflow for creating and validating new skills | Production-Ready |
| [daydream](#daydream) | Insight mining from a note vault with quality scoring, dedup, and knowledge graphs | Production-Ready |
| [dynamic-context-pruning](#dynamic-context-pruning) | Context window management with restorable compression and staged reduction | Production-Ready |
| [having-difficult-conversations](#having-difficult-conversations) | Preparation and practice for difficult workplace conversations | Production-Ready |
| [opencode-zen-delegator](#opencode-zen-delegator) | Unified delegation router for OpenCode Zen and external LLM providers | Production-Ready |
| [performance-optimizer](#performance-optimizer) | Profiler detection, rule scanning, and benchmark harness with baselines | Production-Ready |
| [project-planner](#project-planner) | Structured project planning with templates, critical path, and tracking | Production-Ready |
| [prompt-engineering](#prompt-engineering) | Unified prompt engineering — workflows, EARS methodology, evaluation, model guidance | Production-Ready |
| [remembering-conversations](#remembering-conversations) | Local conversation index with hybrid search and pattern detection | Production-Ready |
| [skill-creator](#skill-creator) | Create, modify, and evaluate skills with template scaffolding and CI/CD | Production-Ready |
| [skill-judge](#skill-judge) | Score skills against official specifications with calibrated rubric | Production-Ready |
| [skill-reviewer](#skill-reviewer) | Batch skill review with security scan, health tracking, and consistency reports | Production-Ready |
| [skills-search](#skills-search) | Unified skill discovery, installation, and management | Production-Ready |
| [strategy-advisor](#strategy-advisor) | Strategy frameworks, decision matrices, scenarios, and templates | Production-Ready |
| [subagent-driven-development](#subagent-driven-development) | Parallel subagent orchestration with task briefs and review packages | Production-Ready |
| [systematic-debugging](#systematic-debugging) | 4-phase root cause debugging with worksheets and pattern library | Production-Ready |
| [telecommunications-expert](#telecommunications-expert) | Telecom network management, billing, 5G, and infrastructure — modular library + CLI | Production-Ready |
| [test-driven-development](#test-driven-development) | RED-GREEN-REFACTOR TDD enforcement with CLI and language support | Production-Ready |
| [trust-psychology](#trust-psychology) | Trust signal analysis, audit, A/B testing, and component library | Production-Ready |
| [verification-before-completion](#verification-before-completion) | Evidence-based verification before claiming completion | Production-Ready |
| [writing-plans](#writing-plans) | Bite-sized implementation plans with validation | Production-Ready |
| [writing-skills](#writing-skills) | Skill authoring with init script, test harness, and registry | Production-Ready |

---

## ai-self-reflection

Metacognitive improvement protocol for AI agents. Two modes: Lightweight (operational friction detection) and Comprehensive (persistent learning with promotion system).

**When to use:**
- A completed task felt mechanically "off"
- User feedback seems misaligned with your intended output
- Repeated failure patterns emerge across sessions
- A strategy worked but may not generalize
- The agent needs to improve its own operating procedure

**Structure:**
```
ai-self-reflection/
├── SKILL.md                  # Unified skill (lightweight + comprehensive modes)
├── README.md                 # Project overview and CLI reference
├── HOWTO.md                  # Integration guide
├── LICENSE                   # MIT License
├── scripts/                  # CLI and core modules
├── references/               # Deep-dive documentation
├── memory/                   # Runtime data (gitignored)
│   └── friction_log.md       # Human-readable reflection log
└── tests/                    # Tests
```

**Quick start:**
```bash
cd ai-self-reflection
python scripts/run_reflection.py --mode lightweight
```

---

## collaborative-skill-engineering

Structured, interactive workflow for AI agents to collaborate with users in defining, developing and validating new skills. Includes scaffolding and validation tooling.

**When to use:**
- Creating a new skill from scratch
- Significantly updating an existing skill
- Validating skill structure against best practices

**Structure:**
```
collaborative-skill-engineering/
├── SKILL.md                          # 8-step collaborative workflow
├── scripts/init_skill.py             # Scaffolds new skill directories
├── scripts/validate_skill.py         # Validates SKILL.md structure + frontmatter
├── references/skill_structure_guide.md  # Directory anatomy and conventions
├── templates/
│   ├── SKILL.md.template             # SKILL.md boilerplate
│   └── scripts/example.py.template   # Argparse script template
└── README.md
```

**Quick start:**
```bash
python scripts/init_skill.py my-new-skill           # Create skill skeleton
python scripts/validate_skill.py my-new-skill/       # Validate structure
```

---

## dynamic-context-pruning

Context engineering for long-horizon agents. Implements restorable compression, KV-cache awareness and staged context reduction (compaction first, summarization only when necessary).

**When to use:**
- Agent sessions exceeding context windows
- Need for reversible compaction and irreversible summarization
- Offloading context to the filesystem
- Monitoring context thresholds

**Structure:**
```
dynamic-context-pruning/
├── SKILL.md                              # 350-line comprehensive guide
├── scripts/
│   ├── compaction.py                     # Reversible context compaction
│   ├── summarization.py                  # Irreversible summarization with schema validation
│   ├── context_monitor.py                # Threshold monitoring and alerts
│   ├── file_offloader.py                 # Offload context to filesystem
│   ├── kv_cache.py                       # KV-cache optimization utilities
│   ├── benchmark_context_reduction.py    # Benchmark reduction strategies
│   ├── test_compaction_reversibility.py  # 11 tests
│   └── test_summarization_schema.py      # 19 tests
├── references/                           # 6 deep-dive docs
├── examples/
│   ├── basic_agent_loop.py
│   ├── full_agent_loop.py
│   └── config_examples/                 # minimal.json, full.json, production.json
├── templates/config_template.json
├── .env.example
└── README.md
```

**Quick start:**
```bash
pip install tiktoken
python scripts/benchmark_context_reduction.py    # See reduction ratios
python -m pytest scripts/test_*.py -v             # Run 30 tests
```

---

## opencode-zen-delegator

Unified delegation router for OpenCode Zen and external LLM providers with automatic fallback, cost optimization and intelligent routing. Merged from `big-pickle-router`, `delegator`, `external-llm-router`, and `rate-limit-router`.

**When to use:**
- Rate limit hit (429 from Zen, OpenRouter, OpenAI or Anthropic)
- Token budget exceeded
- Explicit delegation request
- Complex reasoning tasks
- Cost optimization — route to cheapest capable model
- Provider failover — automatic fallback when primary unavailable

**Structure:**
```
opencode-zen-delegator/
├── SKILL.md                          # Unified delegation router (v2.0.0)
├── scripts/
│   ├── zen_client.py                 # Unified client for all providers
│   ├── router.py                     # Intelligent routing engine
│   ├── monitor.py                    # Token/cost tracking
│   ├── circuit_breaker.py            # Circuit breaker for provider failures
│   ├── health_monitor.py             # Provider health checks
│   ├── context_manager.py            # Context serialization/handoff
│   ├── audit_logger.py               # Delegation audit trail
│   ├── config.py                     # Configuration loading
│   └── test_router.py                # 20+ tests
├── .env.example
└── README.md
```

**Quick start:**
```bash
pip install requests tenacity pyyaml
cp .env.example .env
opencode-zen-delegator delegate "Continue the refactoring..." --context task_context.json
opencode-zen-delegator status --verbose
opencode-zen-delegator route --task "complex reasoning" --explain
```

---

## Environment Variables

---

## Installation

```bash
git clone https://github.com/jarbcs1-prog/skills-2026.git
cd skills-2026

# Install dependencies (varies by skill)
pip install requests tiktoken tenacity pyyaml

# Copy environment templates
cp opencode-zen-delegator/.env.example opencode-zen-delegator/.env
```

---

## Testing

```bash
# ai-self-reflection
cd ai-self-reflection && python -m pytest tests/ -v

# dynamic-context-pruning
cd dynamic-context-pruning && python -m pytest scripts/test_*.py -v

# opencode-zen-delegator
cd opencode-zen-delegator && python -m pytest scripts/test_*.py -v

# having-difficult-conversations
cd having-difficult-conversations && python -m pytest tests/ -v

# project-planner
cd project-planner && python -m pytest tests/ -v

# systematic-debugging
cd systematic-debugging && python -m pytest tests/ -v

# test-driven-development
cd test-driven-development && python -m pytest tests/ -v

# trust-psychology
cd trust-psychology && python -m pytest tests/ -v

# subagent-driven-development
cd subagent-driven-development && python -m pytest tests/ -v

# verification-before-completion
cd verification-before-completion && python -m pytest tests/ -v

# writing-plans
cd writing-plans && python -m pytest tests/ -v

# writing-skills
cd writing-skills && python -m pytest tests/ -v

# skill-creator
cd skill-creator && python -m pytest tests/ -v

# skill-judge
cd skill-judge && python -m pytest tests/ -v

# telecommunications-expert
cd telecommunications-expert && python -m pytest tests/ -v

# brainstorming
cd brainstorming && python -m pytest tests/ -v

# code-quality
cd code-quality && python -m pytest tests/ -v

# code-reviewer
cd code-reviewer && python -m pytest tests/ -v

# daydream
cd daydream && python -m pytest tests/ -v

# performance-optimizer
cd performance-optimizer && python -m pytest tests/ -v

# remembering-conversations
cd remembering-conversations && python -m pytest tests/ -v

# skill-reviewer
cd skill-reviewer && python -m pytest tests/ -v

# skills-search
cd skills-search && python -m pytest tests/ -v

# strategy-advisor
cd strategy-advisor && python -m pytest tests/ -v
```

---

## Repository Structure

```
skills-2026/
├── .gitignore
├── README.md
├── execution/
│   └── execution_plan.md
├── ai-self-reflection/        # Metacognitive improvement protocol
├── brainstorming/             # Design-doc validation + decision matrices
├── code-quality/              # Pre-commit quality gates
├── code-reviewer/             # Rule-engine code reviews + SARIF
├── collaborative-skill-engineering/  # Skill creation toolkit
├── daydream/                  # Insight mining + knowledge graphs
├── dynamic-context-pruning/   # Context window management
├── having-difficult-conversations/   # Conversation preparation
├── opencode-zen-delegator/    # Unified delegation router
├── performance-optimizer/     # Profilers + benchmark harness
├── project-planner/           # Structured project planning
├── prompt-engineering/        # Unified prompt engineering
├── remembering-conversations/ # Local conversation index
├── skill-creator/             # Skill authoring and evaluation
├── skill-judge/               # Skill scoring against specs
├── skill-reviewer/            # Batch skill review
├── skills-search/             # Unified skill discovery
├── strategy-advisor/          # Strategy frameworks + decision tools
├── subagent-driven-development/  # Parallel subagent orchestration
├── systematic-debugging/      # 4-phase root cause debugging
├── telecommunications-expert/ # Telecom NMS/billing/5G library + CLI
├── test-driven-development/   # RED-GREEN-REFACTOR TDD enforcement
├── trust-psychology/          # Trust signal analysis and audit
├── verification-before-completion/  # Evidence before completion claims
├── writing-plans/             # Implementation plan authoring
├── writing-skills/            # Skill authoring toolkit
└── [other skills...]
```

---

## License

Individual skills may carry their own licenses. See `LICENSE` files within each skill directory.
