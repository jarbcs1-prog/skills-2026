---
name: opencode-zen-delegator
description: |
  Unified delegation router for OpenCode Zen and external LLM providers. Handles automatic fallback on rate limits, token budget monitoring, multi-provider routing (Zen, OpenRouter, OpenAI, Anthropic), intelligent model selection by capability/cost and stateful context handoff. Use when: approaching token/rate limits, needing provider failover, delegating complex reasoning tasks or routing to optimal model for task type.
version: "2.0.0"
---

> **Disclaimer:** This plugin is not built by the OpenCode team and is not affiliated with OpenCode in any way. It is an independent community project.

# OpenCode Zen Delegator — Unified Router

Unified delegation system for OpenCode Zen (`opencode/big-pickle`) and external LLM providers with automatic fallback, cost optimization and intelligent routing.

## When to Use

- **Rate limit hit:** 429 from Zen, OpenRouter, OpenAI or Anthropic
- **Token budget exceeded:** Approaching daily/monthly limits
- **Explicit delegation:** User requests "delegate to big-pickle" or "use external model"
- **Complex reasoning:** Tasks benefiting from specialized reasoning models
- **Cost optimization:** Route to cheapest capable model
- **Provider failover:** Automatic fallback when primary unavailable
- **Capability matching:** Select model by required features (reasoning, vision, long-context, code)

---

## Core Capabilities

1. **Multi-Provider Support** — Zen, OpenRouter, OpenAI, Anthropic, custom endpoints
2. **Intelligent Routing** — Task → model matching by capability, cost, health
3. **Automatic Fallback** — Circuit breaker + exponential backoff on 429/5xx
4. **Token/Cost Budgets** — Daily/monthly limits per provider with auto-reset
5. **Stateful Handoff** — Context serialization for seamless delegation
6. **Provider Health** — Latency/error rate monitoring, automatic failover
7. **Audit Logging** — Full delegation trail for compliance

---

## Quick Start

```bash
# Install
pip install requests tenacity pyyaml

# Configure (copy .env.example to .env and add keys)
cp .env.example .env
# Edit .env with your API keys

# Basic delegation — auto-selects best provider
opencode-zen-delegator delegate "Continue the refactoring..." --context task_context.json

# Explicit provider/model
opencode-zen-delegator delegate "Analyze this code" --provider openai --model gpt-4o

# Check status
opencode-zen-delegator status --verbose

# View routing decision
opencode-zen-delegator route --task "complex reasoning" --explain
```

---

## Configuration

### Environment Variables (`.env`)
```bash
# OpenCode Zen
ZEN_API_KEY=your-zen-key
ZEN_DAILY_TOKEN_LIMIT=200000

# OpenRouter
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_DAILY_COST_LIMIT=0.00

# OpenAI
# OPENAI_API_KEY=your-openai-key
# OPENAI_DAILY_COST_LIMIT=100.00

# Anthropic
# ANTHROPIC_API_KEY=your-anthropic-key
# ANTHROPIC_DAILY_COST_LIMIT=50.00
```

### Provider Config (`config.yaml`)
```yaml
version: 2
providers:
  opencode:
    enabled: true
    priority: 1
    base_url: "https://api.opencode.ai/v1"
    models:
      big-pickle:
        capabilities: [reasoning, coding, analysis, long_context]
        cost_per_1k_tokens: 0.0  # Free tier
        max_tokens: 200000
	  deepseek-v4-flash-free:
	    capabilities: [reasoning, coding, analysis, long_context]
        cost_per_1k_tokens: 0.0  # Free tier
        max_tokens: 200000
	  nemotron-3-ultra-free:
	    capabilities: [reasoning, coding, analysis, long_context]
        cost_per_1k_tokens: 0.0  # Free tier
        max_tokens: 1000000
	  mimo-v2.5-free:
	    capabilities: [vision, reasoning, coding, analysis, long_context]
        cost_per_1k_tokens: 0.0  # Free tier
        max_tokens: 200000
    daily_token_limit: 200000
    daily_cost_limit: 0.0

  openrouter:
    enabled: true
    priority: 2
    base_url: "https://openrouter.ai/api/v1"
    models:
      nvidia/nemotron-3-ultra-550b-a55b:free:
        capabilities: [reasoning, coding, analysis]
        cost_per_1k_tokens: 0.0
        max_tokens: 1000000
      cohere/north-mini-code:free:
        capabilities: [reasoning, coding, analysis, long_context]
        cost_per_1k_tokens: 0.0
        max_tokens: 256000
      poolside/laguna-s-2.1:free:
        capabilities: [coding, analysis, vision, long_context]
        cost_per_1k_tokens: 0.0
        max_tokens: 262000
    daily_cost_limit: 0.0

  openai:
    enabled: true
    priority: 3
    base_url: "https://api.openai.com/v1"
    models:
      gpt-4o:
        capabilities: [coding, analysis, vision, long_context]
        cost_per_1k_tokens: 0.005
        max_tokens: 128000
      o1-preview:
        capabilities: [reasoning, coding, analysis]
        cost_per_1k_tokens: 0.015
        max_tokens: 128000
    daily_cost_limit: 100.00

  anthropic:
    enabled: true
    priority: 4
    base_url: "https://api.anthropic.com/v1"
    models:
      claude-sonnet-4-20250514:
        capabilities: [reasoning, coding, analysis, long_context]
        cost_per_1k_tokens: 0.003
        max_tokens: 200000
    daily_cost_limit: 50.00

routing:
  strategy: "capability_cost_health"  # capability_cost | capability_cost_health | cost_only | priority
  fallback_enabled: true
  max_retries: 3
  circuit_breaker:
    failure_threshold: 5
    recovery_timeout: 60
    half_open_requests: 3

delegation:
  auto_trigger_on_limit: true
  context_summary_max_tokens: 5000
  preserve_reasoning: true
  serialize_context: true

health:
  check_interval: 300  # seconds
  timeout: 10
  unhealthy_threshold: 0.5  # error rate
```

---

## Model Capability Registry

| Model | Capabilities | Cost/1K | Context | Best For |
|-------|--------------|---------|---------|----------|
| `opencode/big-pickle` | reasoning, coding, analysis, long_context | Free | 200K | Complex reasoning, debugging |
| `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` | reasoning, coding, analysis | Free | 1M | Heavy reasoning |
| `openrouter/cohere/north-mini-code:free` | reasoning, coding, analysis, long_context | Free | 256K | Balanced reasoning + coding |
| `openrouter/poolside/laguna-s-2.1:free` | coding, analysis, vision, long_context | Free | 262K | Coding, vision, general |
| `opencode/mimo-v2.5-free` | vision, reasoning, coding, analysis | Free | 200K | Reasoning, vision, coding |
| `opencode/deepseek-v4-flash-free` | reasoning, coding, analysis, long_context | Free | 200K | Fast tasks |

---

## CLI Reference

### Delegate Task
```bash
# Auto-route (recommended)
opencode-zen-delegator delegate "your prompt" [--context context.json] [--budget 50000]

# Explicit provider/model
opencode-zen-delegator delegate "prompt" --provider openai --model gpt-4o --system "You are a senior engineer"

# Streaming (default)
opencode-zen-delegator delegate "prompt" --stream

# Non-streaming
opencode-zen-delegator delegate "prompt" --no-stream

# With custom config
opencode-zen-delegator delegate "prompt" --config /path/to/config.yaml
```

### Status & Monitoring
```bash
# Current usage across all providers
opencode-zen-delegator status

# Verbose with per-model breakdown
opencode-zen-delegator status --verbose --format json

# Specific provider
opencode-zen-delegator status --provider openrouter

# Reset daily counters (manual)
opencode-zen-delegator status --reset
```

### Routing Analysis
```bash
# Show which model would be selected for a task
opencode-zen-delegator route --task "complex reasoning" --explain

# List all available models with capabilities
opencode-zen-delegator route --list-models

# Show routing decision for specific requirements
opencode-zen-delegator route --capabilities reasoning,coding --max-cost 0.01
```

### Health & Providers
```bash
# Check all provider health
opencode-zen-delegator health

# Test specific provider
opencode-zen-delegator health --provider zen --test-prompt "Hello"

# View circuit breaker states
opencode-zen-delegator health --circuits
```

### Audit & Costs
```bash
# Delegation audit log
opencode-zen-delegator audit --since 2026-08-01 --format csv

# Cost breakdown
opencode-zen-delegator costs --today --by-model

# Monthly report
opencode-zen-delegator costs --month 2026-08 --format html
```

### Config Management
```bash
# Validate config
opencode-zen-delegator config --validate

# Show effective config (with env overrides)
opencode-zen-delegator config --show

# Generate example config
opencode-zen-delegator config --generate-example > config.yaml
```

---

## Delegation Workflow

### 1. Pre-Delegation Check
```python
# Automatic: checks token budgets, provider health, circuit breakers
# Triggers when: auto_trigger_on_limit=true and limit approached
```

### 2. Context Serialization
```python
# Serializes full context for handoff:
context = {
    "task": "refactor authentication module",
    "history": [...],  # Compressed conversation history
    "files": ["src/auth.py", "tests/test_auth.py"],
    "current_state": "implementing JWT validation",
    "constraints": ["use existing User model", "add rate limiting"],
    "completed_steps": ["created User model", "added password hashing"],
    "tools_available": ["read", "write", "edit", "bash", "grep"],
    "metadata": {
        "session_id": "abc123",
        "delegation_count": 1,
        "total_tokens_used": 45000
    }
}
```

### 3. Model Selection
```python
# Router selects based on strategy:
# capability_cost_health (default):
#   1. Filter by required capabilities
#   2. Filter by budget/cost constraints
#   3. Filter by provider health (circuit breaker)
#   4. Rank by quality/cost ratio
#   5. Return best + fallback chain
```

### 4. Execution with Fallback
```python
for provider in fallback_chain:
    try:
        response = provider.complete(prompt, context, **params)
        # Track usage, cost, latency
        # Handle reasoning_content if available
        return response
    except RateLimitError:
        continue  # Try next in chain
    except ProviderError as e:
        if not fallback_enabled: raise
        continue
raise AllProvidersFailed("All providers exhausted")
```

### 5. Post-Delegation
```python
# Update usage counters
# Log to audit trail
# Return response + metadata (provider, model, tokens, cost, latency)
```

---

## Context Handoff Format

### TaskContext Schema
```json
{
  "task": "string",
  "history": [
    {"role": "user|assistant|system", "content": "string", "tokens": 123}
  ],
  "files": [
    {"path": "src/auth.py", "content": "string", "language": "python"}
  ],
  "current_state": "string",
  "constraints": ["string"],
  "completed_steps": ["string"],
  "tools_available": ["string"],
  "metadata": {
    "session_id": "string",
    "delegation_count": 0,
    "total_tokens_used": 0,
    "budget_remaining": 0
  }
}
```

### Serialization
```bash
# Save context for handoff
opencode-zen-delegator context save --output task_context.json

# Load context
opencode-zen-delegator context load --input task_context.json

# Compress context (for token budget)
opencode-zen-delegator context compress --input task_context.json --max-tokens 10000
```

---

## Scripts (Bundled)

| Script | Purpose |
|--------|---------|
| `scripts/zen_client.py` | Unified client for all providers (OpenAI-compatible) |
| `scripts/router.py` | Intelligent routing engine with capability matching |
| `scripts/monitor.py` | Token/cost tracking with daily/monthly budgets |
| `scripts/circuit_breaker.py` | Circuit breaker pattern for provider failures |
| `scripts/health_monitor.py` | Provider health checks (latency, error rate) |
| `scripts/context_manager.py` | Context serialization, compression, handoff |
| `scripts/audit_logger.py` | Delegation audit trail (JSONL, CSV, SQLite) |
| `scripts/config.py` | Configuration loading with env override |
| `scripts/test_router.py` | 20+ tests: routing, fallback, circuit breaker, budgets |

---

## Integration with Other Skills

### With `opencode-context-pruning`
```python
# Auto-delegate when context exceeds threshold
if context_monitor.needs_delegation():
    delegator.delegate(remaining_task, context=compressed_context)
```

### With `dynamic-context-pruning`
```python
# Offload to cheaper model for summarization
if context_tokens > summarization_trigger:
    cheap_model = router.select_model(capabilities=[], max_cost=0.001)
    summary = cheap_model.summarize(context)
```

### With `verification-before-completion`
```python
# Verify delegation result before claiming completion
verify delegation_output --original-task "refactor auth" --criteria "tests pass, no regressions"
```

---

## Best Practices

1. **Always serialize context** — Prevents work repetition
2. **Set budgets** — Daily cost limits prevent surprise bills
3. **Use capability routing** — Don't hardcode models; specify what you need
4. **Monitor health** — Unhealthy providers auto-failover
5. **Capture reasoning** — For reasoning models, save `reasoning_content`
6. **Audit trail** — Enable for compliance/debugging
7. **Test fallbacks** — Regularly verify fallback chain works

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "All providers failed" | Check API keys, network, provider status pages |
| "Circuit breaker open" | Wait for recovery_timeout, check provider health |
| "Budget exceeded" | Increase limit, optimize prompts, use cheaper model |
| "Context too large" | Use context compress, increase model context window |
| "Rate limited" | Fallback auto-triggers; check fallback chain config |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-08-03 | Unified big-pickle-router, delegator, external-llm-router, rate-limit-router |
| 1.0.0 | 2026-07-15 | Initial external-llm-router |

---

## License

MIT License — Use freely with your AI agents.
