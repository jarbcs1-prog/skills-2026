# Dynamic Context Pruning (OpenCode)

OpenCode-specific context pruning — subset of the root `dynamic-context-pruning` skill optimized for OpenCode's architecture.

## Quick Start

```bash
python -m pytest scripts/ -v
```

## What's Inside

| File | Purpose |
|------|---------|
| `scripts/context_monitor.py` | Threshold monitoring for OpenCode sessions |
| `scripts/compaction.py` | Reversible context reduction |
| `references/opencode_context_engineering.md` | OpenCode-specific context patterns |

## See Also

- `F:\skills_2026\dynamic-context-pruning\` — Full implementation with all scripts, examples, and references
