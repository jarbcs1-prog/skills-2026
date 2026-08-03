# KV-Cache Optimization — Complete Reference

This document provides comprehensive guidance for optimizing Key-Value (KV) cache efficiency in LLM-based agents.

---

## Understanding KV-Cache

### How KV-Cache Works
- **Mechanism**: During attention computation, keys (K) and values (V) for each token are cached
- **Benefit**: Subsequent tokens only compute attention against cached K/V, not full history
- **Speedup**: 2-10x faster inference for long contexts
- **Memory**: Stores K/V for each layer, head, token (~2-4 bytes per parameter per token)

### Cache Invalidation Triggers
Any change to prefix tokens forces full recomputation:
- Token insertion/deletion/modification in prefix
- Token reordering
- Any change to first N tokens where N = prefix length

---

## The Four Core Rules

### Rule 1: Stable Prompt Prefix
**The prefix (first ~30% of context) must be immutable.**

#### Violations
| Violation | Example | Fix |
|-----------|---------|-----|
| Timestamps | `"timestamp": "2026-08-03T10:00:00Z"` in system prompt | Move to metadata, not context |
| Session IDs | `"session_id": "abc-123"` in prefix | Store in metadata |
| Counters | `"turn": 42` in system prompt | Track externally |
| Random values | `"nonce": "x7k9m2"` in prompt | Generate per-request, not in context |
| Dynamic env vars | `"PWD=/home/user"` in prompt | Reference, don't embed |

#### Best Practice
```json
{
  "role": "system",
  "content": "You are a coding assistant. Core instructions only.",
  "_static": true
}
```

---

### Rule 2: Append-Only Context
**Never modify previous messages. Only append.**

#### Violations
| Violation | Example | Fix |
|-----------|---------|-----|
| Edit previous | Change message[5].content | Append correction as new message |
| Delete message | `del context[3]` | Mark hidden, append note |
| Reorder messages | Move message[10] to message[2] | Never reorder |
| Update in-place | `context[i]["tool"] = "new_tool"` | Append new tool_call entry |

#### Correct Pattern
```python
# WRONG - modifies history
context[3]["output"] = "fixed output"

# CORRECT - append correction
context.append({
    "type": "correction",
    "original_index": 3,
    "original_output": "old output",
    "corrected_output": "fixed output",
    "reason": "typo in result"
})
```

#### Tool Definition Stability
```python
# WRONG - tools change each turn
context.append({"type": "tool_definition", "tools": get_current_tools()})

# CORRECT - define once at startup
if not hasattr(agent, '_tools_defined'):
    context.insert(0, {"type": "tool_definition", "tools": all_tools})
    agent._tools_defined = True
```

---

### Rule 3: Deterministic Serialization
**Same data → identical string representation, always.**

#### JSON Serialization
```python
# WRONG - key order non-deterministic
json.dumps({"b": 1, "a": 2})  # '{"b": 1, "a": 2}' or '{"a": 2, "b": 1}'

# CORRECT - sorted keys
json.dumps({"b": 1, "a": 2}, sort_keys=True)  # Always '{"a": 2, "b": 1}'
```

#### Required Settings
```python
json.dumps(
    data,
    sort_keys=True,           # Deterministic key order
    separators=(',', ':'),    # No whitespace variation
    ensure_ascii=False        # Consistent unicode handling
)
```

#### Recursive Sorting
```python
def deterministic_dumps(obj):
    if isinstance(obj, dict):
        return {k: deterministic_dumps(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        return [deterministic_dumps(v) for v in obj]
    return obj

json.dumps(deterministic_dumps(data), sort_keys=True)
```

---

### Rule 4: Explicit Cache Breakpoints
**Signal intentional context resets.**

#### When to Use
| Scenario | Breakpoint Type |
|----------|-----------------|
| Summarization complete | `"summarization_checkpoint"` |
| Major phase transition | `"phase_transition"` |
| Error recovery | `"error_recovery"` |
| User-initiated reset | `"user_reset"` |
| Model switch | `"model_switch"` |

#### Format
```json
{
  "type": "cache_breakpoint",
  "reason": "summarization_checkpoint",
  "tokens_before": 180000,
  "tokens_after": 45000,
  "timestamp": "2026-08-03T10:00:00Z"
}
```

#### Model Behavior
Models should:
1. Recognize breakpoint as cache reset signal
2. Not attend across breakpoint (treat as new context)
3. Use for performance monitoring

---

## Common Cache-Breaking Issues

### 1. Non-Deterministic JSON
**Symptom:** Cache misses on identical logical context
**Detection:** Compare `json.dumps(x, sort_keys=False)` vs `sort_keys=True`
**Fix:** Always use `sort_keys=True`

### 2. Timestamps in Prefix
**Symptom:** Cache invalidates every turn
**Detection:** Search first 30% of context for timestamp patterns
**Fix:** Move timestamps to metadata fields

### 3. Modified Previous Messages
**Symptom:** Cache invalidates on corrections
**Detection:** Track message hashes, detect changes
**Fix:** Append-only pattern (Rule 2)

### 4. Unstable Tool Definitions
**Symptom:** Cache invalidates despite same tools
**Detection:** Hash tool definitions per turn
**Fix:** Define tools once at startup

### 5. Dynamic System Prompt
**Symptom:** System prompt changes slightly each turn
**Detection:** Hash system prompt content
**Fix:** Single static system prompt

### 6. Counter/Turn Numbers in Context
**Symptom:** Every turn changes context
**Detection:** Search for incrementing numbers
**Fix:** Track turn count externally

---

## Optimization Strategies

### 1. Separate Static/Dynamic Context
```
[STATIC PREFIX - CACHED]
├── System prompt (immutable)
├── Core persona/instructions
├── Tool definitions (static)
├── Core constraints/principles
├── Cache breakpoint: "static_prefix_end"

[DYNAMIC SUFFIX - PER TURN]
├── Current task/goal
├── Recent observations (last N)
├── Todo.md recitation
├── Tool call/results (recent)
├── Todo.md recitation
```

**Implementation:**
```python
def build_context(agent):
    static = agent.get_static_prefix()      # Built once, cached
    dynamic = agent.get_dynamic_suffix()    # Built each turn
    return static + dynamic
```

### 2. Context Hashing for Incremental Cache
```python
class ContextCache:
    def __init__(self):
        self.prefix_hashes = {}  # hash -> (prefix_tokens, kv_cache)
    
    def get_or_compute(self, context):
        # Hash first 30% of context
        prefix = context[:len(context)//3]
        prefix_hash = hash(json.dumps(prefix, sort_keys=True))
        
        if prefix_hash in self.prefix_hashes:
            return self.prefix_hashes[prefix_hash].kv_cache
        
        # Compute new cache
        kv_cache = model.compute_kv_cache(prefix)
        self.prefix_hashes[prefix_hash] = CacheEntry(prefix_hash, prefix, kv_cache)
        return kv_cache
```

### 3. Batching & Chunking
For contexts > model window:
```python
def process_long_context(context, model_window):
    chunks = split_into_chunks(context, model_window * 0.8)
    summaries = []
    
    for chunk in chunks[:-1]:
        summary = summarize_chunk(chunk)
        summaries.append(summary)
    
    # Process final chunk with all summaries
    final_context = summaries + chunks[-1]
    return model.generate(final_context)
```

---

## Platform-Specific KV-Cache Behavior

### OpenCode (Prompt Cache)
- **Feature**: OpenCode maintains prompt cache across turns
- **Optimization**: Stable prefix up to 50% of context
- **Breakpoint**: Explicit `/compact` command triggers cache reset
- **Monitoring**: `/kv-cache validate` checks for issues

### Generic Models
- **Feature**: Standard KV-cache per request
- **Optimization**: Stable prefix as large as possible
- **Breakpoint**: Any context modification
- **Monitoring**: Manual validation via `kv-cache` command

---

## Monitoring & Validation

### Automated Validation
```python
# In agent loop
issues = kv_optimizer.validate(context_history)
if issues:
    logger.warning(f"KV-cache issues: {len(issues)}")
    for issue in issues:
        logger.warning(f"  [{issue.severity}] {issue.issue_type}: {issue.message}")
    
    # Auto-fix if enabled
    if config.kv_cache.auto_fix:
        context_history = kv_optimizer.fix(context_history)
```

### Validation Checks
| Check | Severity | Auto-Fixable |
|-------|----------|--------------|
| Non-deterministic JSON | Warning | Yes (sort_keys) |
| Timestamps in prefix | Critical | Yes (remove) |
| Modified messages | Critical | Yes (restore from offload) |
| Unstable tool defs | Critical | Yes (deduplicate) |
| Unstable system prompt | Critical | Yes (keep first only) |
| Dynamic content in prefix | Warning | Yes (extract) |

### Metrics to Track
| Metric | Target |
|--------|--------|
| Cache hit rate | >95% |
| Prefix stability | 100% (no changes) |
| Recomputation rate | <5% of turns |
| Prefix length | Max possible within window |

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Slow inference after N turns | Cache invalidation | Check validation issues |
| Inconsistent outputs | Cache corruption | Full context reset |
| Memory OOM | Prefix too large | Reduce static prefix |
| Context drift | Attention loss | Recite todo.md, inject goals |
| Tool hallucination | Unstable tool defs | Freeze tool definitions |

---

## Configuration Reference

```json
{
  "kv_cache": {
    "enforce_stable_prefix": true,
    "append_only": true,
    "deterministic_json": true,
    "max_prefix_tokens": 50000,
    "auto_fix": true,
    "validation_interval": 10,
    "breakpoint_types": [
      "summarization_checkpoint",
      "phase_transition",
      "error_recovery",
      "user_reset"
    ]
  }
}
```

---

## Testing KV-Cache Efficiency

```bash
# Validate context
dynamic-context-pruning kv-cache --validate --context history.json

# Fix issues
dynamic-context-pruning kv-cache --validate --fix --context history.json --output fixed.json

# Benchmark
dynamic-context-pruning benchmark --iterations 100
```

**Expected Results:**
- Validation: <50ms for 200K token context
- Fix: <100ms for 200K token context
- Cache hit rate: >95% in production