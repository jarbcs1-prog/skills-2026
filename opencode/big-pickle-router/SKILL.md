---
name: big-pickle-router
description: "Route tasks to the opencode/big-pickle model via OpenCode Zen API. Use when: delegating complex reasoning tasks, approaching token limits, or when explicitly requested to use big-pickle."
---

# Big Pickle Router

Routes tasks to the `opencode/big-pickle` reasoning model via the OpenCode Zen API.

## When to Trigger

1. **Approaching Limits:** System warning about token or daily request limits.
2. **Explicit Request:** User asks to "use big-pickle" or "delegate to opencode/big-pickle".
3. **Complex Reasoning:** Tasks requiring extended chain-of-thought that benefit from a specialized reasoning model.

## Workflow

### 1. Save Current State
Use `delegate_manager.py` to save context before handoff.

### 2. Check Token Budget
Use `token_monitor.py` to verify remaining quota:
```bash
python scripts/token_monitor.py <tokens_used_this_call>
```

### 3. Execute via Big Pickle
```bash
python scripts/big_pickle_agent.py "YOUR_PROMPT" [context.json]
```

## Configuration

Set your API key as an environment variable:
```bash
export OPENCODE_API_KEY="your-key-here"
```

Or create a `.env` file (see `.env.example`).

## Bundled Resources

| Script | Purpose |
|--------|---------|
| `scripts/big_pickle_agent.py` | Call the big-pickle model |
| `scripts/delegate_manager.py` | Save/load task context |
| `scripts/token_monitor.py` | Track daily token usage |
| `scripts/verify_new_key.py` | Test API key against endpoints |

## Notes
- The `opencode/big-pickle` model provides `reasoning_content` before its final answer.
- Token limit is configurable via `DAILY_TOKEN_LIMIT` env var (default: 1300).
