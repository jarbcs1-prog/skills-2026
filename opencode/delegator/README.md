# Opencode Zen Delegator

Delegate tasks to `opencode/big-pickle` (Big Pickle) via the Opencode Zen API when approaching token limits or for complex reasoning tasks.

## Quick Start

```bash
# 1. Set your API key
cp .env.example .env
# Edit .env with your key

# 2. Send a prompt
python scripts/big_pickle_agent.py "Explain the Observer pattern"

# 3. Send with context
python scripts/big_pickle_agent.py "Continue the refactoring" task_context.json
```

## Install

Requires Python 3.10+ and `requests`:

```bash
pip install requests
```

## Scripts

### `big_pickle_agent.py` — LLM Client

```bash
# Basic usage
python scripts/big_pickle_agent.py "Your prompt here"

# With prior context
python scripts/big_pickle_agent.py "Next step" context.json
```

**Output:**
- Prints `--- REASONING ---` block (if the model returns reasoning content)
- Prints `--- RESPONSE ---` block with the final answer

### `delegate_manager.py` — Context Manager

Utility for saving and loading task context during handoffs.

## Environment Variables

```bash
OPENCODE_API_KEY=your-opencode-zen-api-key
```

## How It Works

1. **Save state** — Use `delegate_manager.py` to serialize current task context
2. **Prepare brief** — Write a concise prompt with goal, next step, and constraints
3. **Execute** — Run `big_pickle_agent.py` with the prompt and context file
4. **Receive** — Big Pickle returns reasoning + response
