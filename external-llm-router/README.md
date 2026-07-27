# External LLM Router

Delegate coding tasks to external LLM providers (OpenCode Zen, OpenAI, OpenRouter, Anthropic) with automatic retry, usage tracking, and per-day limits.

## Quick Start

```bash
# 1. Copy and edit the env file
cp .env.example .env
# Fill in at least OPENCODE_API_KEY

# 2. Send a prompt
python scripts/agent.py \
  --url https://opencode.ai/zen/v1/chat/completions \
  --model opencode/big-pickle \
  --prompt "Explain the Observer pattern in Python"

# 3. Track usage
python scripts/monitor.py --file daily_usage.json --add 1500 --limit 100000
```

## Install

No dependencies beyond Python 3.10+ and `requests`:

```bash
pip install requests
```

## Scripts

### `agent.py` — LLM Client

```bash
# Basic usage
python scripts/agent.py --url URL --model MODEL --prompt "Hello"

# With conversation history
python scripts/agent.py --url URL --model MODEL --prompt "Continue" \
  --context context.json

# With Anthropic endpoint (auto-detected from URL)
python scripts/agent.py \
  --url https://api.anthropic.com/v1/messages \
  --model claude-sonnet-4-20250514 \
  --prompt "Summarize this code" --system "You are a helpful assistant"

# Reset usage counter before sending
python scripts/agent.py --url URL --model MODEL --prompt "Start" \
  --reset-usage daily_usage.json
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--url` | API endpoint (required) |
| `--model` | Model ID (required) |
| `--prompt` | User prompt (required) |
| `--api-key` | API key (falls back to env var) |
| `--env-var` | Env var name for key (default: `OPENCODE_API_KEY`) |
| `--context` | Path to JSON conversation history |
| `--system` | System prompt (Anthropic only) |
| `--max-tokens` | Max response tokens (default: 4096) |
| `--reset-usage` | Reset a usage file before sending |

**Features:**
- Auto-detects OpenAI vs Anthropic from the URL
- Retries on 429/5xx with exponential backoff (3 attempts)
- Loads `.env` files automatically
- Captures `reasoning_content` from reasoning models

### `monitor.py` — Usage Tracker

```bash
# Add tokens and check limit
python scripts/monitor.py --file usage.json --add 1500 --limit 100000

# Check current usage
python scripts/monitor.py --file usage.json --status --limit 100000

# Reset counter
python scripts/monitor.py --file usage.json --reset
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--file` | Usage file path (default: `daily_usage.json`) |
| `--add N` | Add N tokens to counter |
| `--status` | Show current usage without modifying |
| `--reset` | Zero out the counter |
| `--limit N` | Daily token limit (default: 100000) |

**Features:**
- Auto-resets when the date changes
- Exits with code 1 when limit is exceeded
- Atomic read/write to avoid corruption

## Provider Setup

See [references/provider_setup.md](references/provider_setup.md) for detailed setup instructions for each provider (API key acquisition, endpoints, model lists).

## Environment Variables

```bash
OPENCODE_API_KEY=...   # OpenCode Zen
OPENAI_API_KEY=...     # OpenAI
OPENROUTER_API_KEY=... # OpenRouter
ANTHROPIC_API_KEY=...  # Anthropic
```

The `.env` file in the skill root is loaded automatically.
