# Big-Pickle Router

Routes tasks to the `opencode/big-pickle` reasoning model via the OpenCode Zen API.

## Quick Start

```bash
# 1. Set your API key
export OPENCODE_API_KEY="your-key-here"
# Or copy .env.example to .env and fill in

# 2. Verify your key works
python scripts/verify_new_key.py

# 3. Call big-pickle
python scripts/big_pickle_agent.py "Explain quantum entanglement"
```

## Setup

1. Set `OPENCODE_API_KEY` as an environment variable or in a `.env` file.
2. Optionally set `DAILY_TOKEN_LIMIT` (default: 1300).

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/big_pickle_agent.py` | Call the big-pickle model with a prompt and optional context |
| `scripts/delegate_manager.py` | Save/load conversation context for handoff |
| `scripts/token_monitor.py` | Track daily token usage against your limit |
| `scripts/verify_new_key.py` | Test your API key against all endpoints |

## Usage Examples

```bash
# Check token usage
python scripts/token_monitor.py 500

# Override daily limit
python scripts/token_monitor.py 500 --limit 2000

# Call with context file
python scripts/big_pickle_agent.py "Summarize this" context.json

# Test key with --key flag
python scripts/verify_new_key.py --key "your-key"
```

## How It Works

1. When approaching token limits or on explicit request, save current state via `delegate_manager.py`.
2. Check remaining budget with `token_monitor.py`.
3. Hand off the task to `big_pickle_agent.py`, which calls the `opencode/big-pickle` model.
4. The model returns both `reasoning_content` (chain-of-thought) and the final `content`.

## Files

```
big-pickle-router/
  SKILL.md              # Agent skill definition
  .env.example          # Environment variable template
  README.md             # This file
  scripts/
    __init__.py
    big_pickle_agent.py  # API client
    delegate_manager.py  # Context save/load
    token_monitor.py     # Token tracking
    verify_new_key.py    # Key verification
    test_*.py            # Endpoint test scripts
```
