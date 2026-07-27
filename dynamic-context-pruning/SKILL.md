---
name: dynamic-context-pruning
description: |
  Dynamic Context Pruning Skill. Implements context engineering with restorable compression, KV-cache awareness and staged context reduction. Use this skill for long-horizon agents exceeding context windows, implementing reversible compaction and irreversible summarization, offloading context to the filesystem, monitoring context thresholds and ensuring KV-cache friendly append-only context with deterministic serialization. This skill provides production-ready context pruning following these six key techniques: KV-cache optimization, tool masking via logit manipulation, file system as external memory with restorable compression, staged reduction (compaction first, summarization only when needed), attention management via todo.md recitation and controlled diversity to prevent context rot.
---

# Dynamic Context Pruning Skill

This skill implements context engineering principles for dynamic context pruning with **restorable compression**, **staged reduction** and **KV-cache awareness**.

## Core Philosophy

Following these principles:
- **Context is not a transcript** — it's a carefully managed working memory
- **Compaction over summarization** — reversible first, irreversible only when necessary
- **File system as ultimate context** — unlimited, persistent, directly operable
- **Restorable compression** — drop content, keep references (URLs, paths, IDs)
- **KV-cache friendly** — stable prefixes, append-only, deterministic serialization

## Progressive Disclosure Levels

| Level | Content | Load Trigger | Token Cost |
|-------|---------|--------------|------------|
| 1: Metadata | Skill name, description, version | Agent startup | ~100 tokens |
| 2: Instructions | This SKILL.md (core workflows) | Skill triggered via `/dynamic-context-pruning` | <5k tokens |
| 3: Resources | Scripts, schemas, references | Referenced in instructions | On-demand only |

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
```

---

## Workflows

### 1. Context Monitoring (`monitor`)

Continuously track context length against existing thresholds:

```python
# scripts/context_monitor.py
from context_monitor import ContextMonitor

monitor = ContextMonitor(
    hard_limit=256_000,           # Model hard limit
    pre_rot_threshold=100_000,    # Degradation begins
    compaction_trigger=150_000,   # Trigger compaction
    summarization_trigger=175_000 # Trigger summarization
)

# Check current status
status = monitor.check_context(context_tokens=current_token_count)
# Returns: {"action": "none|compact|summarize|critical", "tokens": int, "percent": float}

# Get detailed metrics
metrics = monitor.get_metrics()
```

**Thresholds:**
- **Hard limit**: 256K tokens (model maximum)
- **Pre-rot threshold**: 100K-125K (where attention degradation begins)
- **Compaction trigger**: ~80% of pre-rot (start compaction early)
- **Summarization trigger**: ~90% of pre-rot (only when compaction fails)

### 2. Compaction (`compact`)

Reversible context reduction — drop detail, keep structure:

```python
# scripts/compaction.py
from compaction import Compactor

compactor = Compactor(
    keep_recent_full=5,        # Keep last N tool calls in full detail
    compact_ratio=0.5,         # Compact oldest 50%
    preserve_structure=True    # Keep tool call/response structure
)

# Compact context
compacted = compactor.compact(context_history)
# Returns: compacted_context, offloaded_data (for file storage)

# Restore from compacted + offloaded
restored = compactor.restore(compacted_context, offloaded_file_path)
```

**Compaction Strategies:**
- `token_budget`: Allocate token budget across history segments
- `age_based`: Compact oldest N% of tool calls
- `importance_based`: Score tool calls by relevance, compact lowest
- `hybrid`: Combine age + importance (Manus default)

### 3. Summarization (`summarize`)

Irreversible but structured — use schemas, not free-form:

```python
# scripts/summarization.py
from summarization import Summarizer, SummarySchema

# Define structured summary schema
schema = SummarySchema(
    fields=[
        "files_modified",
        "user_goals", 
        "current_state",
        "pending_actions",
        "errors_encountered",
        "key_decisions"
    ],
    required=["user_goals", "current_state"]
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
    base_path=".agent_context",
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
# Returns: {"path": ".agent_context/tool_calls_0-25.jsonl.gz", "url": "file://...", "tokens": 45231}

# Restore from reference
restored = offloader.restore(reference["path"])
```

**Restorable Compression Rules:**
- Web content → drop HTML, keep URL
- Document content → drop text, keep file path
- Tool outputs → drop verbose output, keep structured result
- Always preserve: URLs, file paths, IDs, structured data

### 5. KV-Cache Optimization (`kv-cache`)

Ensure context is KV-cache friendly:

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

**KV-Cache Rules:**
1. Stable prompt prefix — no timestamps, no dynamic content
2. Append-only context — never modify previous actions/observations
3. Deterministic serialization — use `json.dumps(sort_keys=True)`
4. Explicit cache breakpoints — mark where cache should reset

---

## Configuration

Create `.agent_context_config.json` in your project root:

```json
{
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
    "importance_weights": {
      "user_goals": 1.0,
      "errors": 0.9,
      "key_decisions": 0.8,
      "tool_outputs": 0.5,
      "intermediate_steps": 0.3
    }
  },
  "summarization": {
    "schema": "agent_default",
    "keep_recent_full": 3,
    "model": "opencode/big-pickle"
  },
  "offloading": {
    "base_path": ".agent_context",
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

## Integration with Agent Loops

```python
# In your agent's main loop
from context_monitor import ContextMonitor
from compaction import Compactor
from summarization import Summarizer
from file_offloader import FileOffloader

monitor = ContextMonitor.from_config(".agent_context_config.json")
compactor = Compactor.from_config(".agent_context_config.json")
summarizer = Summarizer.from_config(".agent_context_config.json")
offloader = FileOffloader.from_config(".agent_context_config.json")

async def agent_step(context_history):
    # 1. Check context health
    status = monitor.check_context(len(estimate_tokens(context_history)))
    
    if status["action"] == "compact":
        # 2. Compact oldest context
        compacted, offloaded = compactor.compact(context_history)
        # 3. Offload to filesystem
        ref = offloader.offload(offloaded, metadata={"phase": "compaction"})
        # 4. Replace with compacted + reference
        context_history = compacted + [{"type": "context_reference", "ref": ref}]
        
    elif status["action"] == "summarize":
        # 2. Summarize with structured schema
        summary = summarizer.summarize(context_history[:-3])  # Keep last 3
        # 3. Offload full context for recovery
        ref = offloader.offload(context_history[:-3], metadata={"phase": "summarization"})
        # 4. Replace with summary + reference
        context_history = [{"type": "summary", "data": summary}, {"type": "context_reference", "ref": ref}] + context_history[-3:]
    
    return context_history
```

---

## References

- `references/context_engineering_principles.md` — Six techniques deep dive
- `references/compaction_strategies.md` — Detailed compaction algorithms
- `references/summarization_schemas.md` — Structured summary schemas
- `references/kv_cache_optimization.md` — KV-cache friendly patterns
- `references/file_offloading_patterns.md` — Restorable compression rules

---

## Scripts

| Script | Purpose | Entry Point |
|--------|---------|-------------|
| `scripts/context_monitor.py` | Threshold monitoring & alerts | `ContextMonitor` class |
| `scripts/compaction.py` | Reversible context reduction | `Compactor` class |
| `scripts/summarization.py` | Structured irreversible summarization | `Summarizer` class |
| `scripts/file_offloader.py` | Filesystem offloading with references | `FileOffloader` class |
| `scripts/kv_cache.py` | KV-cache validation & fixing | `KVCacheOptimizer` class |

---

## Example Usage

See `examples/` directory:
- `examples/basic_agent_loop.py` — Minimal integration example
- `examples/full_agent_loop.py` — Complete agent loop
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
| 1.0.0 | 2026-07-02 | Initial release with full context engineering implementation |

---

## License

MIT License — Use freely with your AI agents.
