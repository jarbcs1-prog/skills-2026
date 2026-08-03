---
name: dynamic-context-pruning
description: |
  Dynamic Context Pruning Skill with dual-mode support (Generic + OpenCode). Implements context engineering with restorable compression, KV-cache awareness, staged context reduction, timestamp-based message hiding, head/tail protection, and repeated tool pruning. Use for long-horizon agents exceeding context windows. Features: reversible compaction, irreversible structured summarization, filesystem offloading, threshold monitoring, KV-cache optimization, and platform-specific strategies.
version: "2.0.0"
---

# Dynamic Context Pruning — Unified (Generic + OpenCode)

Unified context engineering with **platform modes** (Generic / OpenCode / Auto-detect). Implements restorable compression, staged reduction, KV-cache awareness, and platform-specific optimizations.

## When to Use

- Long-horizon agents exceeding context windows
- Implementing reversible compaction and irreversible summarization
- Offloading context to filesystem with restorable references
- Monitoring context thresholds with automated actions
- Ensuring KV-cache friendly append-only context
- **OpenCode-specific**: timestamp-based hiding, head/tail protection, repeated tool pruning
- **Generic**: token-budget, age-based, importance-based, hybrid compaction

---

## Core Philosophy

- **Context is not a transcript** — it's carefully managed working memory
- **Compaction over summarization** — reversible first, irreversible only when necessary
- **File system as ultimate context** — unlimited, persistent, directly operable
- **Restorable compression** — drop content, keep references (URLs, paths, IDs)
- **KV-cache friendly** — stable prefixes, append-only, deterministic serialization
- **Tiered Reduction** — prevent garbage context from entering window (Head/Tail protection)

---

## Platform Modes

| Mode | Compaction Strategy | Summarization Schema | Thresholds | Special Features |
|------|---------------------|---------------------|------------|------------------|
| `generic` | hybrid (age + importance) | agent_default (6 fields) | 256K/100K/150K/175K | 4 strategies, flexible weights |
| `opencode` | timestamp_hiding + head_tail | opencode_5_heading (5 fields) | 200K/100K/150K/175K | Timestamp hiding, head/tail protection, repeated tool pruning, error preservation |
| `auto` | Detects from environment | Auto-selects | Auto-selects | Best of both |

### Auto-Detection Logic
```python
def detect_platform() -> Platform:
    if os.environ.get("OPENCODE_SESSION_ID"): return Platform.OPENCODE
    if os.environ.get("AGENT_FRAMEWORK") == "opencode": return Platform.OPENCODE
    if Path(".opencode").exists(): return Platform.OPENCODE
    return Platform.GENERIC
```

---

## Quick Start

```bash
# Trigger the skill
/dynamic-context-pruning

# Or use specific workflows
/dynamic-context-pruning monitor      # Start context monitoring
/dynamic-context-pruning compact      # Run compaction on current context
/dynamic-context-pruning summarize    # Run summarization with structured output
/dynamic-context-pruning offload      # Offload context to filesystem
/dynamic-context-pruning thresholds   # Check/update context thresholds
/dynamic-context-pruning platform     # Show/change platform mode
```

---

## Workflows

### 1. Context Monitoring (`monitor`)

```python
# scripts/context_monitor.py
from context_monitor import ContextMonitor

# Generic mode
monitor = ContextMonitor(
    hard_limit=256_000,
    pre_rot_threshold=100_000,
    compaction_trigger=150_000,
    summarization_trigger=175_000
)

# OpenCode mode (lower hard limit for standard models)
monitor = ContextMonitor(
    hard_limit=200_000,
    pre_rot_threshold=100_000,
    compaction_trigger=150_000,
    summarization_trigger=175_000
)

# Check current status
status = monitor.check_context(context_tokens=current_token_count)
# Returns: {"action": "none|compact|summarize|critical", "tokens": int, "percent": float}

# Get detailed metrics
metrics = monitor.get_metrics()
# Returns: tokens_used, percent, trend, predicted_exhaustion, time_to_trigger
```

**Thresholds by Platform:**
| Platform | Hard Limit | Pre-Rot | Compaction | Summarization |
|----------|------------|---------|------------|---------------|
| Generic | 256K | 100K | 150K | 175K |
| OpenCode | 200K | 100K | 150K | 175K |

---

### 2. Compaction (`compact`)

Reversible context reduction — drop detail, keep structure:

```python
# scripts/compaction.py
from compaction import Compactor, OpenCodeCompactor, CompactionStrategy

# Generic strategies
compactor = Compactor(
    strategy=CompactionStrategy.HYBRID,  # TOKEN_BUDGET, AGE_BASED, IMPORTANCE_BASED, HYBRID
    keep_recent_full=5,
    compact_ratio=0.5,
    preserve_structure=True,
    importance_weights={
        "user_goals": 1.0,
        "errors": 0.9,
        "key_decisions": 0.8,
        "tool_outputs": 0.5,
        "intermediate_steps": 0.3
    }
)

# OpenCode-specific strategies
compactor = OpenCodeCompactor(
    strategy=CompactionStrategy.TIMESTAMP_HIDING,  # TIMESTAMP_HIDING, HEAD_TAIL_PROTECTION, REPEATED_TOOL_PRUNING, ERROR_PRESERVATION
    keep_recent_full=5,
    protect_zones=["head", "tail"],
    max_tool_output_tokens=2000
)

# Compact context
compacted, offloaded = compactor.compact(context_history)
# Returns: compacted_context, offloaded_data (for file storage)

# Restore from compacted + offloaded
restored = compactor.restore(compacted_context, offloaded_file_path)
```

**Compaction Strategies:**

| Strategy | Mode | Description |
|----------|------|-------------|
| `token_budget` | Generic | Allocate token budget across history segments |
| `age_based` | Generic | Compact oldest N% of tool calls |
| `importance_based` | Generic | Score by relevance, compact lowest |
| `hybrid` | Generic | Combine age + importance (default) |
| `timestamp_hiding` | OpenCode | OpenCode native non-destructive timestamp-based hiding |
| `head_tail_protection` | OpenCode | Token budget per tool output, keep head/tail, prune middle |
| `repeated_tool_pruning` | OpenCode | Identify repeated tool calls, keep only most recent |
| `error_preservation` | OpenCode | Prune errored inputs after N turns, always preserve errors |

---

### 3. Summarization (`summarize`)

Irreversible but structured — use schemas, not free-form:

```python
# scripts/summarization.py
from summarization import Summarizer, SummarySchema, SCHEMAS

# Generic schema (6 fields)
schema = SCHEMAS["agent_default"]  # files_modified, user_goals, current_state, pending_actions, errors_encountered, key_decisions

# OpenCode schema (5 fields) — OpenCode standard
schema = SCHEMAS["opencode_5_heading"]  # current_state, completed_actions, pending_actions, key_decisions, errors_encountered

# Minimal schema (2 fields)
schema = SCHEMAS["minimal"]  # current_state, pending_actions

summarizer = Summarizer(
    schema=schema,
    keep_recent_full=3,
    model="opencode/big-pickle"
)

# Generate structured summary
summary = summarizer.summarize(context_history)
# Returns: structured dict matching schema, not free text

# Verify summary quality
validation = summarizer.validate(summary, context_history)
```

**Schemas:**

| Schema | Fields | Required | Use Case |
|--------|--------|----------|----------|
| `agent_default` | files_modified, user_goals, current_state, pending_actions, errors_encountered, key_decisions | user_goals, current_state | General agents |
| `opencode_5_heading` | current_state, completed_actions, pending_actions, key_decisions, errors_encountered | current_state, pending_actions | OpenCode agents |
| `minimal` | current_state, pending_actions | current_state, pending_actions | Token-critical |

**Key Principle**: Never use free-form summarization. Always use structured outputs with explicit schemas.

---

### 4. File Offloading (`offload`)

Offload context to filesystem with restorable references:

```python
# scripts/file_offloader.py
from file_offloader import FileOffloader

offloader = FileOffloader(
    base_path=".agent_context",        # Generic: .agent_context | OpenCode: .opencode_context
    compression="gzip",
    index_format="jsonl"
)

# Offload context segment
reference = offloader.offload(
    data=context_segment,
    metadata={
        "type": "tool_calls",
        "range": "0-25",
        "summary": "Initial research phase",
        "platform": "generic|opencode"
    }
)
# Returns: {"path": ".agent_context/tool_calls_0-25.jsonl.gz", "url": "file://...", "tokens": 45231}

# Restore from reference
restored = offloader.restore(reference["path"])
```

**Restorable Compression Rules (Both Platforms):**
- Web content → drop HTML, keep URL
- Document content → drop text, keep file path
- Tool outputs → drop verbose output, keep structured result
- Always preserve: URLs, file paths, IDs, structured data

---

### 5. KV-Cache Optimization (`kv-cache`)

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

**KV-Cache Rules (Both Platforms):**
1. Stable prompt prefix — no timestamps, no dynamic content
2. Append-only context — never modify previous actions/observations
3. Deterministic serialization — use `json.dumps(sort_keys=True)`
4. Explicit cache breakpoints — mark where cache should reset

---

## Configuration

Create `.agent_context_config.json` in project root:

```json
{
  "platform": "auto",
  "thresholds": {
    "hard_limit": 200000,
    "pre_rot_threshold": 100000,
    "compaction_trigger": 150000,
    "summarization_trigger": 175000
  },
  "compaction": {
    "strategy": "hybrid",
    "keep_recent_full": 5,
    "compact_ratio": 0.5,
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
    "schema": "auto",
    "keep_recent_full": 3,
    "model": "opencode/big-pickle"
  },
  "offloading": {
    "base_path": "auto",
    "compression": "gzip",
    "index_format": "jsonl"
  },
  "kv_cache": {
    "enforce_stable_prefix": true,
    "append_only": true,
    "deterministic_json": true
  },
  "opencode": {
    "compaction_strategy": "timestamp_hiding",
    "protect_zones": ["head", "tail"],
    "max_tool_output_tokens": 2000,
    "summarization_schema": "opencode_5_heading",
    "repeated_tool_pruning": true,
    "error_preservation": true
  }
}
```

**Platform-Specific Defaults:**
- `platform: "auto"` — auto-detects from environment
- `schema: "auto"` — selects `opencode_5_heading` for OpenCode, `agent_default` for Generic
- `base_path: "auto"` — `.opencode_context` for OpenCode, `.agent_context` for Generic

---

## Integration with Agent Loops

```python
# scripts/integration.py
from context_monitor import ContextMonitor
from compaction import Compactor, OpenCodeCompactor
from summarization import Summarizer, SCHEMAS
from file_offloader import FileOffloader
from platform import detect_platform, Platform

def create_components(config_path: str = ".agent_context_config.json"):
    platform = detect_platform()
    
    if platform == Platform.OPENCODE:
        compactor = OpenCodeCompactor.from_config(config_path)
        schema = SCHEMAS["opencode_5_heading"]
        base_path = ".opencode_context"
    else:
        compactor = Compactor.from_config(config_path)
        schema = SCHEMAS["agent_default"]
        base_path = ".agent_context"
    
    monitor = ContextMonitor.from_config(config_path)
    summarizer = Summarizer(schema=schema, keep_recent_full=3, model="opencode/big-pickle")
    offloader = FileOffloader(base_path=base_path, compression="gzip", index_format="jsonl")
    
    return monitor, compactor, summarizer, offloader

async def agent_step(context_history, config_path=".agent_context_config.json"):
    monitor, compactor, summarizer, offloader = create_components(config_path)
    
    status = monitor.check_context(len(estimate_tokens(context_history)))
    
    if status["action"] == "compact":
        compacted, offloaded = compactor.compact(context_history)
        ref = offloader.offload(offloaded, metadata={"phase": "compaction", "platform": platform.value})
        context_history = compacted + [{"type": "context_reference", "ref": ref}]
        
    elif status["action"] == "summarize":
        summary = summarizer.summarize(context_history[:-3])
        ref = offloader.offload(context_history[:-3], metadata={"phase": "summarization", "platform": platform.value})
        context_history = [{"type": "summary", "data": summary}, {"type": "context_reference", "ref": ref}] + context_history[-3:]
    
    return context_history
```

---

## CLI Reference

```bash
# Platform management
dynamic-context-pruning platform --show
dynamic-context-pruning platform --set generic|opencode|auto

# Core workflows
dynamic-context-pruning monitor --config .agent_context_config.json
dynamic-context-pruning compact --context history.json --output compacted.json --platform auto
dynamic-context-pruning summarize --context history.json --schema auto --platform auto
dynamic-context-pruning offload --data context_segment.json --metadata meta.json
dynamic-context-pruning thresholds --show --update --config .agent_context_config.json

# KV-Cache
dynamic-context-pruning kv-cache --validate --fix --context history.json

# Config
dynamic-context-pruning config --validate --config .agent_context_config.json
dynamic-context-pruning config --generate --platform generic|opencode --output .agent_context_config.json

# Testing
dynamic-context-pruning test --all
dynamic-context-pruning test --compaction-reversibility
dynamic-context-pruning test --summarization-schema
dynamic-context-pruning benchmark --iterations 100
```

---

## References

- `references/context_engineering_principles.md` — Six techniques deep dive
- `references/compaction_strategies.md` — All 8 compaction algorithms
- `references/summarization_schemas.md` — All 3 structured summary schemas
- `references/kv_cache_optimization.md` — KV-cache friendly patterns
- `references/file_offloading_patterns.md` — Restorable compression rules
- `references/opencode_specific.md` — OpenCode-specific techniques (timestamp hiding, head/tail, repeated tool pruning)

---

## Scripts

| Script | Purpose | Entry Points |
|--------|---------|--------------|
| `scripts/context_monitor.py` | Threshold monitoring & alerts | `ContextMonitor` class |
| `scripts/compaction.py` | Reversible context reduction (8 strategies) | `Compactor`, `OpenCodeCompactor` classes |
| `scripts/summarization.py` | Structured irreversible summarization (3 schemas) | `Summarizer` class, `SCHEMAS` dict |
| `scripts/file_offloader.py` | Filesystem offloading with references | `FileOffloader` class |
| `scripts/kv_cache.py` | KV-cache validation & fixing | `KVCacheOptimizer` class |
| `scripts/integration.py` | Agent loop integration helpers | `create_components`, `agent_step` |
| `scripts/platform.py` | Platform detection | `detect_platform`, `Platform` enum |
| `scripts/token_estimator.py` | Token estimation (tiktoken) | `estimate_tokens` function |

---

## Testing

```bash
# Run all unit tests
python -m pytest scripts/ -v

# Test compaction reversibility (all strategies)
python scripts/test_compaction_reversibility.py

# Test summarization schema validation (all schemas)
python scripts/test_summarization_schema.py

# Test platform detection
python scripts/test_platform_detection.py

# Test OpenCode-specific strategies
python scripts/test_opencode_strategies.py

# Benchmark context reduction
python scripts/benchmark_context_reduction.py
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-08-03 | Unified Generic + OpenCode modes, 8 compaction strategies, 3 schemas, auto-detection |
| 1.0.0 | 2026-07-02 | Initial Generic release |
| 1.0.0 | 2026-07-11 | Initial OpenCode release (separate skill) |

---

## License

MIT License — Use freely with your AI agents.