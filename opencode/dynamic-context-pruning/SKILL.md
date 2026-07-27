---
name: opencode-context-pruning
description: |
  Dynamic Context Pruning Skill customized for OpenCode. Implements OpenCode-specific context engineering with timestamp-based message hiding, cache-friendly prefix preservation and agent-tiered compaction. Use this skill for long-horizon OpenCode sessions exceeding context windows, implementing reversible compaction and irreversible summarization, offloading context to the filesystem, monitoring context thresholds and ensuring KV-cache friendly append-only context with deterministic serialization. This skill provides production-ready context pruning optimized for OpenCode's architecture and its ecosystem plugins.
---

# OpenCode Dynamic Context Pruning Skill

This skill implements OpenCode-specific context engineering principles for dynamic context pruning with **timestamp-based message hiding**, **staged reduction** and **KV-cache awareness**. It is designed to work alongside or replace OpenCode's native compaction agent and complement the official DCP plugin.

## Core Philosophy

Following OpenCode and general agent architecture principles:
- **Context is not a transcript** — it's a carefully managed working memory
- **Compaction over summarization** — reversible first (hiding), irreversible only when necessary (summarization)
- **File system as ultimate context** — unlimited, persistent, directly operable
- **Restorable compression** — drop content, keep references (URLs, paths, IDs)
- **KV-cache friendly** — stable prefixes, append-only, deterministic serialization
- **Tiered Reduction** — prevent "garbage" context from entering the window in the first place (Head/Tail protection)

## Progressive Disclosure Levels

| Level | Content | Load Trigger | Token Cost |
|-------|---------|--------------|------------|
| 1: Metadata | Skill name, description, version | Agent startup | ~100 tokens |
| 2: Instructions | This SKILL.md (core workflows) | Skill triggered via `/opencode-context-pruning` | <5k tokens |
| 3: Resources | Scripts, schemas, references | Referenced in instructions | On-demand only |

---

## Quick Start

```bash
# Trigger the skill
/opencode-context-pruning

# Or use specific workflows
/opencode-context-pruning monitor      # Start context monitoring
/opencode-context-pruning compact      # Run timestamp-based compaction on current context
/opencode-context-pruning summarize    # Run summarization with structured output
/opencode-context-pruning offload      # Offload context to filesystem
/opencode-context-pruning thresholds   # Check/update context thresholds
```

---

## Workflows

### 1. Context Monitoring (`monitor`)

Continuously track context length against OpenCode-specific thresholds:

```python
# scripts/context_monitor.py
from context_monitor import ContextMonitor

monitor = ContextMonitor(
    hard_limit=200_000,           # Model hard limit (e.g. OpenCode Zen large context)
    pre_rot_threshold=100_000,    # Degradation begins (standard large model limit)
    compaction_trigger=150_000,   # Trigger timestamp-based compaction early
    summarization_trigger=175_000 # Trigger summarization
)

# Check current status
status = monitor.check_context(context_tokens=current_token_count)
# Returns: {"action": "none|compact|summarize|critical", "tokens": int, "percent": float}

# Get detailed metrics
metrics = monitor.get_metrics()
```

**Thresholds (OpenCode defaults):**
- **Hard limit**: 200K tokens (model maximum)
- **Pre-rot threshold**: 100K (standard large model limit where attention degradation begins)
- **Compaction trigger**: ~78% of pre-rot (start compaction early to preserve KV-cache)
- **Summarization trigger**: ~90% of pre-rot (only when compaction fails)

### 2. Timestamp-Based Compaction (`compact`)

Reversible context reduction using OpenCode's native approach — hide old messages by timestamp, protect recent context:

```python
# scripts/compaction.py
from compaction import OpenCodeCompactor

compactor = OpenCodeCompactor(
    keep_recent_full=5,             # Keep last N tool calls in full detail
    protect_zones=["head", "tail"], # Protect start and end of tool outputs
    max_tool_output_tokens=2000     # Token budget per tool output
)

# Compact context
compacted = compactor.compact(context_history)
# Returns: compacted_context, hidden_data (for file storage/hiding)

# Restore from compacted + hidden
restored = compactor.restore(compacted_context, hidden_file_path)
```

**OpenCode Compaction Strategies:**
- `timestamp_hiding`: OpenCode's native non-destructive timestamp-based message hiding
- `head_tail_protection`: Token budgeting per tool output, keeping critical context (head) and results/errors (tail), pruning the middle
- `repeated_tool_pruning`: Identifies repeated tool calls (same tool, same arguments) and keeps only the most recent output
- `error_preservation`: Prunes errored tool call inputs after configurable turns, but always preserves error messages

### 3. Summarization (`summarize`)

Irreversible but structured — use schemas, not free-form:

```python
# scripts/summarization.py
from summarization import Summarizer, SummarySchema

# Define structured summary schema (OpenCode 5-heading approach)
schema = SummarySchema(
    fields=[
        "current_state",
        "completed_actions",
        "pending_actions",
        "key_decisions",
        "errors_encountered"
    ],
    required=["current_state", "pending_actions"]
)

summarizer = Summarizer(
    schema=schema,
    keep_recent_full=3,          # Preserve last 3 tool calls verbatim
    model="opencode/big-pickle"  # Or your preferred model
)

# Generate structured summary
summary = summarizer.summarize(context_history)
# Returns: structured dict matching schema, not free text

# Verify summary quality
validation = summarizer.validate(summary, context_history)
```

**Key Principle**: Never use free-form summarization. Always use structured outputs with explicit schemas.

### 4. File Offloading (`offload`)

Offload context to filesystem with restorable references:

```python
# scripts/file_offloader.py
from file_offloader import FileOffloader

offloader = FileOffloader(
    base_path=".opencode_context",
    compression="gzip",
    index_format="jsonl"
)

# Offload context segment
reference = offloader.offload(
    data=context_segment,
    metadata={
        "type": "tool_calls",
        "range": "0-25",
        "summary": "Initial research phase"
    }
)
# Returns: {"path": ".opencode_context/tool_calls_0-25.jsonl.gz", "url": "file://...", "tokens": 45231}

# Restore from reference
restored = offloader.restore(reference["path"])
```

**Restorable Compression Rules (OpenCode):**
- Web content → drop HTML, keep URL
- Document content → drop text, keep file path
- Tool outputs → drop verbose output, keep structured result
- Always preserve: URLs, file paths, IDs, structured data

### 5. KV-Cache Optimization (`kv-cache`)

Ensure context is KV-cache friendly, leveraging OpenCode's Prompt Cache:

```python
# scripts/kv_cache.py
from kv_cache import KVCacheOptimizer

optimizer = KVCacheOptimizer()

# Validate context for cache efficiency
issues = optimizer.validate(context_history)
# Returns list of cache-breaking issues:
# - Non-deterministic JSON serialization
# - Timestamps in prefix
# - Modified previous messages
# - Unstable tool definitions

# Fix issues automatically
fixed_context = optimizer.fix(context_history)
# Returns: cache-friendly context
```

**KV-Cache Rules (OpenCode):**
1. Stable prompt prefix — no timestamps, no dynamic content (OpenCode tries to avoid modifying the first half of the message sequence)
2. Append-only context — never modify previous actions/observations
3. Deterministic serialization — use `json.dumps(sort_keys=True)`
4. Explicit cache breakpoints — mark where cache should reset

---

## Configuration

Create `.opencode_context_config.json` in your project root:

```json
{
  "thresholds": {
    "hard_limit": 200000,
    "pre_rot_threshold": 100000,
    "compaction_trigger": 150000,
    "summarization_trigger": 175000
  },
  "compaction": {
    "strategy": "timestamp_hiding",
    "keep_recent_full": 5,
    "protect_zones": ["head", "tail"],
    "max_tool_output_tokens": 2000,
    "importance_weights": {
      "user_goals": 1.0,
      "errors": 0.9,
      "key_decisions": 0.8,
      "tool_outputs": 0.5,
      "intermediate_steps": 0.3
    }
  },
  "summarization": {
    "schema": "opencode_default",
    "keep_recent_full": 3,
    "model": "opencode/big-pickle"
  },
  "offloading": {
    "base_path": ".opencode_context",
    "compression": "gzip",
    "index_format": "jsonl"
  },
  "kv_cache": {
    "enforce_stable_prefix": true,
    "append_only": true,
    "deterministic_json": true
  }
}
```

---

## Integration with OpenCode Agent Loop

```python
# In your OpenCode agent's main loop or plugin
from context_monitor import ContextMonitor
from compaction import OpenCodeCompactor
from summarization import Summarizer
from file_offloader import FileOffloader

monitor = ContextMonitor.from_config(".opencode_context_config.json")
compactor = OpenCodeCompactor.from_config(".opencode_context_config.json")
summarizer = Summarizer.from_config(".opencode_context_config.json")
offloader = FileOffloader.from_config(".opencode_context_config.json")

async def opencode_agent_step(context_history):
    # 1. Check context health
    status = monitor.check_context(len(estimate_tokens(context_history)))
    
    if status["action"] == "compact":
        # 2. Compact oldest context using timestamp hiding
        compacted, hidden = compactor.compact(context_history)
        # 3. Offload hidden data to filesystem
        ref = offloader.offload(hidden, metadata={"phase": "compaction"})
        # 4. Replace with compacted + reference
        context_history = compacted + [{"type": "context_reference", "ref": ref}]
        
    elif status["action"] == "summarize":
        # 2. Summarize with structured schema (5-heading)
        summary = summarizer.summarize(context_history[:-3])  # Keep last 3
        # 3. Offload full context for recovery
        ref = offloader.offload(context_history[:-3], metadata={"phase": "summarization"})
        # 4. Replace with summary + reference
        context_history = [{"type": "summary", "data": summary}, {"type": "context_reference", "ref": ref}] + context_history[-3:]
    
    return context_history
```

---

## References

- `references/opencode_context_engineering.md` — OpenCode's specific techniques deep dive
- `references/compaction_strategies.md` — Detailed compaction algorithms (Head/Tail, Timestamp)
- `references/summarization_schemas.md` — Structured summary schemas (5-heading)
- `references/kv_cache_optimization.md` — KV-cache friendly patterns
- `references/file_offloading_patterns.md` — Restorable compression rules

---

## Scripts

| Script | Purpose | Entry Point |
|--------|---------|-------------|
| `scripts/context_monitor.py` | Threshold monitoring & alerts | `ContextMonitor` class |
| `scripts/compaction.py` | Reversible context reduction (timestamp hiding) | `OpenCodeCompactor` class |
| `scripts/summarization.py` | Structured irreversible summarization | `Summarizer` class |
| `scripts/file_offloader.py` | Filesystem offloading with references | `FileOffloader` class |
| `scripts/kv_cache.py` | KV-cache validation & fixing | `KVCacheOptimizer` class |

---

## Example Usage

See `examples/` directory:
- `examples/basic_opencode_loop.py` — Minimal integration example
- `examples/full_opencode_loop.py` — Complete OpenCode-style agent loop
- `examples/config_examples/` — Configuration templates

---

## Testing

```bash
# Run unit tests
python -m pytest scripts/ -v

# Test compaction reversibility
python scripts/test_compaction_reversibility.py

# Test summarization schema validation
python scripts/test_summarization_schema.py

# Benchmark context reduction
python scripts/benchmark_context_reduction.py
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-11 | Initial release with OpenCode-specific context engineering implementation |

---

## License

MIT License — Use freely with your OpenCode AI agents.
