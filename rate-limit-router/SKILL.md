---
name: opencode-rate-limit-router
description: "Automatic API rate-limit fallback between OpenCode Zen and OpenRouter. Use when hitting 429 errors, rate limits or when explicitly delegating to avoid rate limits."
---

# Opencode Rate Limit Router

Automatically reroutes API calls to the alternate provider when a 429 is received, with exponential backoff.

## When to Use

1. **Rate limit hit:** When a request returns 429 from either OpenCode Zen or OpenRouter
2. **Explicit delegation:** User asks to "use rate limit router" or "try the other API"
3. **Long sessions:** When context pruning isn't enough and you need provider failover

## Setup

1. Copy `.env.example` to `.env` and fill in your API keys
2. Install dependency: `pip install requests`
3. Ensure `config.json` exists in the skill root (default model mappings provided)

## Usage

```bash
# Basic — tries Zen first, falls back to OpenRouter
python scripts/rate_limit_router.py "your prompt" --model big-pickle

# With system prompt
python scripts/rate_limit_router.py "Summarize" --model deepseek-v4-flash-free --system "Be concise"

# Verbose — shows which API served the response
python scripts/rate_limit_router.py "Hello" --model big-pickle -v

# Non-streaming
python scripts/rate_limit_router.py "Hello" --model hy3-free --no-stream

# Custom config
RATE_LIMIT_CONFIG=/path/to/config.json python scripts/rate_limit_router.py "Hello" --model big-pickle
```

## Model Mapping

Opencode Zen models automatically fallback to their OpenRouter equivalents:

| Opencode Zen Model | OpenRouter Fallback |
|---|---|
| `big-pickle` | `nvidia/nemotron-3-super-120b-a12b:free` |
| `deepseek-v4-flash-free` | `qwen/qwen3-next-80b-a3b-instruct:free` |
| `mimo-v2.5-free` | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` |
| `ling-3.0-flash-free` | `tencent/hy3:free` |
| `nemotron-3-ultra-free` | `nvidia/nemotron-3-ultra-550b-a55b:free` |
| `north-mini-code-free` | `cohere/north-mini-code:free` |
| `laguna-s-2.1-free` | `poolside/laguna-s-2.1:free` |

OpenRouter models also fallback to Zen when rate-limited.

## Configuration

API keys are read from environment variables (not config files):
- `ZEN_API_KEY`: Your OpenCode Zen API key
- `OPENROUTER_API_KEY`: Your OpenRouter API key

Model mappings and backoff settings are in `config.json`.

## Bundled Resources

- `scripts/rate_limit_router.py`: Main router with retry + exponential backoff
- `scripts/test_router.py`: 18 tests covering routing, fallback, and error handling
- `config.json`: Model mapping and backoff configuration
- `.env.example`: Environment variable template
