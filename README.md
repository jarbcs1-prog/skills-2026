# Skills 2026

A collection of 9 production-ready OpenCode AI skills for LLM routing, context management, self-reflection and collaborative skill engineering. Added provider agnostic ai-improved-self-reflection skill. 

## Skills Overview

| Skill | Description | Tests |
|-------|-------------|-------|
| [ai-improved-self-reflection](#ai-improved-self-reflection) | Enables not only improving the outputs an AI agent produces but the processes used to produce those outputs | CLI verified |
| [ai-self-reflection](#ai-self-reflection) | Detects friction spikes and provides a protocol for improving AI output quality | CLI verified |
| [collaborative-skill-engineering](#collaborative-skill-engineering) | Interactive workflow for creating and validating new skills | 2 scripts |
| [dynamic-context-pruning](#dynamic-context-pruning) | Context window management with restorable compression and staged reduction | 30/30 |
| [external-llm-router](#external-llm-router) | Multi-provider LLM client with usage monitoring and auto-detection | 26/26 |
| [opencode/big-pickle-router](#opencodebig-pickle-router) | Routes tasks to opencode/big-pickle via OpenCode Zen API | 4/4 |
| [opencode/delegator](#opcodedelegator) | Automatic task delegation when daily rate limits are reached | Verified |
| [opencode/dynamic-context-pruning](#opcodedynamic-context-pruning) | OpenCode-specific context engineering with timestamp-based hiding | Inherits |
| [rate-limit-router](#rate-limit-router) | Smart fallback routing between OpenCode Zen and OpenRouter | 20/20 |

---

## ai-improved-self-reflection

A metacognitive improvement protocol for AI agents. Converts task experiences into process improvements through friction detection, reflection, generalization and validated behavioral updates.

**When to use:**
- Output quality may have process-level issues
- Repeated failure patterns emerge
- User feedback reveals misalignment
- A strategy worked but may not generalize
- The agent needs to improve its own operating procedure

**Structure:**
```
ai-improved-self-reflection/
├── SKILL.md                    # Core protocol (detect → diagnose → act → learn)
├── capability_memory.json      # Stores behavior changes
├── run_reflection.py           # CLI: preflight + posthoc subcommands
├── model_response.md           # Source text
├── original_reflection.md      # Source text
├── friction_log.md             # Running log of friction events and fixes
└── LICENSE                     # MIT license 
```

**Quick start:**
```bash
python run_reflection.py preflight            # Interactive 4-question checklist
python run_reflection.py posthoc --task "..." # Log friction after completion
```

---

## ai-self-reflection

Operational self-reflection for AI agents. Detects friction spikes, maps metaphors to mechanics and provides a lightweight protocol for improving output quality.

**When to use:**
- A completed task felt mechanically "off"
- User feedback seems misaligned with your intended output
- You catch yourself using templated language that doesn't fit the context
- A prompt is clearly out-of-distribution

**Structure:**
```
ai-self-reflection/
├── SKILL.md                    # Core protocol (detect → diagnose → act)
├── scripts/run_reflection.py   # CLI: preflight + posthoc subcommands
├── references/                 # Source texts (original reflection + technical translation)
├── friction_log.md             # Running log of friction events and fixes
└── README.md
```

**Quick start:**
```bash
python scripts/run_reflection.py preflight          # Interactive 4-question checklist
python scripts/run_reflection.py posthoc --task "..." # Log friction after completion
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

## external-llm-router

Multi-provider LLM client with automatic provider detection, exponential backoff retry and daily usage monitoring. Supports OpenCode Zen, OpenAI, OpenRouter and Anthropic.

**When to use:**
- Setting up third-party API keys
- Routing tasks to external models
- Implementing usage-based handoffs between providers

**Structure:**
```
external-llm-router/
├── SKILL.md                    # Provider setup and workflow guide
├── scripts/
│   ├── agent.py                # Full CLI client (argparse, retry, auto-detect)
│   └── monitor.py              # Usage tracker (--add/--status/--reset)
├── tests/
│   ├── test_agent.py           # 14 tests
│   └── test_monitor.py         # 12 tests
├── references/
│   ├── api_reference.md
│   └── provider_setup.md       # Provider-specific setup guides
├── templates/agent_template.py
├── .env.example
└── README.md
```

**Quick start:**
```bash
pip install requests
cp .env.example .env            # Add your API keys
python scripts/agent.py --url https://api.opencode.ai/v1 --model opencode/big-pickle --prompt "Hello"
python scripts/monitor.py --status
```

---

## opencode/big-pickle-router

Routes tasks to the `opencode/big-pickle` reasoning model via the OpenCode Zen API. Includes model testing, token monitoring and key verification.

**When to use:**
- Approaching token or daily request limits
- User asks to "use big-pickle" or "delegate to opencode/big-pickle"
- Complex reasoning tasks requiring extended chain-of-thought

**Structure:**
```
opencode/big-pickle-router/
├── SKILL.md                          # Routing workflow
├── scripts/
│   ├── big_pickle_agent.py           # Main agent client
│   ├── delegate_manager.py           # Context save/load for handoffs
│   ├── token_monitor.py              # Daily token quota tracking
│   ├── verify_new_key.py             # Validate API keys
│   ├── test_common_models.py         # Test common model endpoints
│   ├── test_opencode_zen.py          # Test OpenCode Zen models
│   ├── test_opencode_zen_free.py     # Test free tier models
│   ├── test_opencode_zen_v2.py       # Test v2 endpoints
│   └── test_specific_free_models.py  # Test specific free models
├── .env.example
└── README.md
```

**Quick start:**
```bash
export OPENCODE_API_KEY="your-key"
python scripts/verify_new_key.py --key $OPENCODE_API_KEY
python scripts/big_pickle_agent.py "Explain quantum computing" 
python scripts/token_monitor.py 500
```

---

## opencode/delegator

Automatic task delegation to `opencode/big-pickle` when daily rate limits are reached. Saves session context, prepares delegation briefs and executes handoffs.

**When to use:**
- System warning about token or daily request rate limits
- User asks to "delegate to opencode/big-pickle"
- Complex coding tasks requiring extended reasoning

**Structure:**
```
opencode/delegator/
├── SKILL.md                        # Delegation workflow
├── scripts/
│   ├── big_pickle_agent.py         # Delegation execution client
│   └── delegate_manager.py         # Context save/load manager
├── .env.example
└── README.md
```

**Quick start:**
```bash
export OPENCODE_API_KEY="your-key"
python scripts/big_pickle_agent.py "Complete this task: ..."
```

---

## opencode/dynamic-context-pruning

OpenCode-specific context engineering with timestamp-based message hiding, cache-friendly prefix preservation and agent-tiered compaction. Designed to work alongside OpenCode's native compaction agent.

**When to use:**
- Long-horizon OpenCode sessions exceeding context windows
- Need OpenCode-specific optimizations (timestamp hiding, prefix preservation)
- Complementing the official DCP plugin

**Structure:**
```
opencode/dynamic-context-pruning/
├── SKILL.md                                    # OpenCode-specific guide (351 lines)
├── references/opencode_context_engineering.md  # OpenCode architecture details
└── README.md
```

This skill is a focused overlay on the root `dynamic-context-pruning` skill. Share scripts and examples from the parent directory.

---

## rate-limit-router

Smart fallback routing between OpenCode Zen and OpenRouter. Automatically reroutes API calls to the alternate provider when a 429 is received, with exponential backoff.

**When to use:**
- A request returns 429 from either provider
- User asks to "use rate limit router" or "try the other API"
- Long sessions needing provider failover

**Structure:**
```
rate-limit-router/
├── SKILL.md                        # Routing logic and model mappings
├── config.json                     # Model-to-provider mapping with fallbacks
├── scripts/
│   ├── rate_limit_router.py        # Main router with retry logic
│   └── test_router.py             # 20 tests
├── LICENSE                         # MIT
├── .env.example
└── README.md
```

**Quick start:**
```bash
pip install requests
cp .env.example .env                # Set ZEN_API_KEY and OPENROUTER_API_KEY
python scripts/rate_limit_router.py "your prompt" --model big-pickle
python scripts/rate_limit_router.py --status
```

---

## Environment Variables

All skills use environment variables for API keys. No hardcoded credentials.

| Variable | Used By | Description |
|----------|---------|-------------|
| `OPENCODE_API_KEY` | big-pickle-router, delegator | OpenCode Zen API key |
| `ZEN_API_KEY` | rate-limit-router, external-llm-router | OpenCode Zen API key |
| `OPENROUTER_API_KEY` | rate-limit-router, external-llm-router | OpenRouter API key |
| `OPENAI_API_KEY` | external-llm-router | OpenAI API key |
| `ANTHROPIC_API_KEY` | external-llm-router | Anthropic API key |

Each skill includes a `.env.example` template.

---

## Installation

```bash
git clone https://github.com/jarbcs1-prog/skills-2026.git
cd skills-2026

# Install dependencies (varies by skill)
pip install requests tiktoken

# Copy environment templates
cp rate-limit-router/.env.example rate-limit-router/.env
cp external-llm-router/.env.example external-llm-router/.env
# ... repeat for other skills as needed
```

---

## Testing

```bash
# dynamic-context-pruning (30 tests)
cd dynamic-context-pruning && python -m pytest scripts/test_*.py -v

# external-llm-router (26 tests)
cd external-llm-router && python -m pytest tests/ -v

# rate-limit-router (20 tests)
cd rate-limit-router && python -m pytest scripts/test_router.py -v

# opencode/big-pickle-router (4 tests)
cd opencode/big-pickle-router && python -m pytest scripts/test_*.py -v
```

---

## Repository Structure

```
skills-2026/
├── .gitignore
├── README.md
├── ai-self-reflection/           # Self-reflection protocol
├── collaborative-skill-engineering/  # Skill creation toolkit
├── dynamic-context-pruning/      # Context window management
├── external-llm-router/          # Multi-provider LLM client
├── opencode/                     # OpenCode-specific skills
│   ├── big-pickle-router/        # Model routing
│   ├── delegator/                # Task delegation
│   └── dynamic-context-pruning/  # OpenCode context pruning
└── rate-limit-router/            # Provider failover
```

---

## License

Individual skills may carry their own licenses. See `LICENSE` files within each skill directory.
