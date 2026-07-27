# Rate Limit Router

Automatic API rate-limit fallback between OpenCode Zen and OpenRouter with exponential backoff.

## Quick Start

```bash
# Install dependency
pip install requests

# Set up API keys
cp .env.example .env
# Edit .env with your keys

# Run
export ZEN_API_KEY=your-key
export OPENROUTER_API_KEY=your-key
python scripts/rate_limit_router.py "Hello" --model big-pickle -v
```

## What's Inside

| File | Purpose |
|------|---------|
| `scripts/rate_limit_router.py` | Main router — tries primary provider, falls back on 429 |
| `scripts/test_router.py` | 18 tests covering routing, fallback, errors |
| `config.json` | Model mappings and backoff settings |
| `.env.example` | API key template |

## How It Works

1. Detects provider from model ID (contains `:` = OpenRouter, no `:` = Zen)
2. Calls primary provider
3. On 429/5xx: retries with exponential backoff (1s → 2s → 4s → 8s → 16s cap)
4. If primary exhausted: falls back to alternate provider
5. On 401/403: fails immediately (no retry for auth errors)

## Dependencies

- Python 3.10+
- `requests` (`pip install requests`)

## License

MIT
