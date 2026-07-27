---
name: external-llm-router
description: "Configure and manage external LLM providers (OpenCode Zen, OpenRouter, etc.) with automatic delegation based on token limits. Use when: setting up third-party API keys, routing tasks to external models or implementing usage-based handoffs."
---

# External LLM Router

This skill provides a framework for agents to delegate work to external LLM providers when internal limits are reached or when specific model capabilities are required.

## Core Capabilities

1.  **Provider Setup:** Configure API keys and endpoints for providers like OpenCode Zen, OpenRouter, Anthropic or OpenAI.
2.  **Usage Monitoring:** Track token consumption against a daily threshold.
3.  **Stateful Handoff:** Save current task context and seamlessly transition to an external model.

## Workflow

### 1. Configure Provider
- Identify the API endpoint and model ID.
- Store the API key securely as an environment variable or in a configuration file.

### 2. Monitor Limits
Use the bundled monitor script to track usage:
```bash
# Check current usage
python scripts/monitor.py --status

# Add tokens after a call
python scripts/monitor.py --add 1500

# Reset daily counter
python scripts/monitor.py --reset

# Custom limit (default: 100000)
python scripts/monitor.py --status --limit 50000
```

### 3. Delegate Task
When limits are reached, use the agent script to continue the work:
```bash
# OpenCode Zen
python scripts/agent.py --url "https://api.opencode.ai/v1/chat/completions" \
  --model "opencode/big-pickle" \
  --prompt "Continue the refactoring..." \
  --context task_context.json

# OpenAI
python scripts/agent.py --url "https://api.openai.com/v1/chat/completions" \
  --model "gpt-4o" \
  --prompt "Analyze this code" \
  --env-var OPENAI_API_KEY

# Anthropic
python scripts/agent.py --url "https://api.anthropic.com/v1/messages" \
  --model "claude-sonnet-4-20250514" \
  --prompt "Review this PR" \
  --system "You are a senior engineer" \
  --env-var ANTHROPIC_API_KEY
```

## Bundled Resources

- **`scripts/agent.py`**: A generic client for OpenAI and Anthropic-compatible endpoints. Auto-detects provider from URL. Supports retry with exponential backoff.
- **`scripts/monitor.py`**: A utility to track cumulative token usage with daily auto-reset. Exits with code 1 when limit exceeded (useful in CI).
- **`references/api_reference.md`**: Documentation for common provider endpoints and model IDs.
- **`references/provider_setup.md`**: Step-by-step setup for each provider.

## Best Practices
- **Reasoning Models:** When using reasoning-heavy models (like `opencode/big-pickle`), ensure you capture and display the `reasoning_content` if available.
- **Context Preservation:** Always include the `context.json` to avoid repeating work.
- **Daily Reset:** Clear the usage tracking file at the start of each day to reset the limit.
