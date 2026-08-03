# Context Engineering Principles — Six Core Techniques

This document provides deep dives into the six foundational techniques of context engineering that power the Dynamic Context Pruning Skill.

---

## 1. KV-Cache Optimization — Stable Prefixes & Append-Only Context

### The Problem
LLM inference uses Key-Value (KV) caches to avoid recomputing attention for previous tokens. When context is modified (timestamps added, messages reordered, tools redefined), the cache becomes invalid, forcing full recomputation — dramatically slowing inference.

### Core Principles

#### Stable Prompt Prefix
- **No timestamps** in system prompt or early context
- **No dynamic content** (counters, versions, random IDs) in first ~30% of context
- **Deterministic serialization** — always `json.dumps(data, sort_keys=True)`

#### Append-Only Context
- **Never modify** previous messages/observations
- **Never delete** entries — mark hidden or offload instead
- **Append corrections** as new entries, not edits
- **Stable tool definitions** — define once at startup, never modify

#### Deterministic Serialization
```python
# Always use for any context serialization
json.dumps(data, sort_keys=True, separators=(',', ':'))
```

#### Explicit Cache Breakpoints
Mark where KV-cache should reset (e.g., after summarization):
```python
context.append({"type": "cache_breakpoint", "reason": "summarization"})
```

### Impact
- **Cache hit rate**: >95% with stable prefixes vs <50% with dynamic content
- **Inference speed**: 2-10x faster for long contexts
- **Memory efficiency**: Shared prefix caches across requests

---

## 2. Tool Masking via Logit Manipulation

### The Problem
Agents with many tools waste tokens and attention evaluating irrelevant tools. Traditional solution: remove tools (breaks capability). Better: bias model away from irrelevant tools.

### Technique: Logit Biasing
Instead of removing tools, adjust selection probabilities:

```python
# Conceptual (actual implementation depends on model API)
logit_bias = {
    "tool_read_file": +2.0,      # Encourage for exploration
    "tool_write_file": -1.0,     # Discourage unless needed
    "tool_delete_file": -5.0,    # Strongly discourage
}
```

### Implementation Strategies

#### Context-Aware Masking
- **Exploration phase**: Boost `read`, `search`, `grep`
- **Implementation phase**: Boost `write`, `edit`
- **Verification phase**: Boost `test`, `lint`
- **Never phase**: Mask `delete`, `bash -rf` unless explicit

#### Dynamic Tool Sets
- Load tool definitions per-phase
- Use tool descriptions to guide (not force) selection
- Never hard-remove — bias instead

### Benefits
- Preserves full capability
- Reduces token waste on tool evaluation
- Improves decision quality

---

## 3. File System as External Memory with Restorable Compression

### Core Philosophy
**Context window is limited; filesystem is unlimited.** Offload cold context to disk with perfect restoration.

### Restorable Compression Rules

| Content Type | Drop | Keep (Reference) |
|--------------|------|------------------|
| Web content (HTML) | Full HTML | URL + title + summary |
| Documents (PDF, DOCX) | Full text | File path + key excerpts |
| Tool outputs | Verbose output | Structured result + metadata |
| Large JSON | Full object | Schema + key fields |
| **Always Preserve** | — | URLs, file paths, IDs, structured data, error messages |

### Offload Format
```
.agent_context/
  index.jsonl           # JSONL index of all offloads
  tool_calls_0-25.jsonl.gz
  tool_calls_26-50.jsonl.gz
  ...
```

### Index Entry Schema
```json
{
  "path": ".agent_context/tool_calls_0-25.jsonl.gz",
  "url": "file:///abs/path",
  "tokens": 45231,
  "sha256": "abc123...",
  "metadata": {
    "type": "tool_calls",
    "range": "0-25",
    "summary": "Initial research phase",
    "timestamp": "2026-08-03T10:00:00Z",
    "platform": "generic"
  }
}
```

### Restoration Guarantee
- **Lossless**: SHA256 verification on restore
- **Atomic**: Full context or nothing
- **Incremental**: Can restore single segments

---

## 4. Staged Reduction — Compaction First, Summarization Only When Needed

### Hierarchy of Reduction

```
Context Grows
    │
    ▼
┌─────────────────────────────────────┐
│ 1. MONITOR                          │
│    Check thresholds continuously    │
└─────────────┬───────────────────────┘
              │
       ┌──────┴──────┐
       ▼             ▼
   Pre-Rot      Compaction
   Threshold    Trigger
  (100K-125K)   (150K)
       │             │
       ▼             ▼
   Warn agent   REVERSIBLE
                COMPACTION
                (drop detail,
                 keep structure)
       │
       ▼
   Summarization
   Trigger (175K)
       │
       ▼
   IRREVERSIBLE
   SUMMARIZATION
   (structured,
   schema-based)
```

### Stage 1: Compaction (Reversible)
- **Drop detail, keep structure**
- Token budgeting per segment
- Hide old entries (timestamp hiding)
- Prune verbose tool outputs (head/tail)
- Deduplicate repeated tool calls
- **Always restorable** from offloaded data

### Stage 2: Summarization (Irreversible)
- **Structured output only** — never free-form
- Schema-defined fields (5-6 fields)
- Keep last 3 tool calls verbatim
- **Validated** against original context

### Threshold Defaults

| Platform | Hard Limit | Pre-Rot | Compaction | Summarization |
|----------|------------|---------|------------|---------------|
| Generic | 256K | 100K | 150K | 175K |
| OpenCode | 200K | 100K | 150K | 175K |

**Rule:** Compaction at ~75% of pre-rot; Summarization at ~90% of pre-rot. Early action preserves quality.

---

## 5. Attention Management via Todo.md Recitation

### The Problem
Long contexts cause "attention drift" — agent loses focus on primary objectives.

### Solution: Structured Attention Anchors

#### Todo.md as Attention Focal Point
```markdown
# Todo

## Active
- [ ] Refactor auth module to JWT
- [ ] Add rate limiting

## Completed
- [x] Read current auth code
- [x] Design JWT schema

## Blocked
- [ ] Waiting for API key
```

#### Recitation Protocol
Every N turns (configurable, default 5):
1. Read `todo.md`
2. Verbally recite: "Current focus: Refactor auth module. Next: Add rate limiting."
3. Update status if needed
4. Use as context for next decision

#### Benefits
- Re-centers agent on objectives
- Prevents rabbit holes
- Makes progress visible
- Surfaces blockers early

---

## 6. Controlled Diversity to Prevent Context Rot

### The Problem
Context "rots" when:
- Too narrow (only recent errors)
- Too stale (old decisions forgotten)
- Too homogeneous (same tool repeated)

### Solution: Diversity Management

#### Diversity Dimensions
| Dimension | Target | Mechanism |
|-----------|--------|-----------|
| **Temporal** | Balance recent/historical | Age-based compaction weights |
| **Semantic** | Cover goals, errors, decisions, tools | Importance weighting |
| **Tool usage** | Prevent single-tool loops | Repeated tool pruning |
| **Outcome types** | Balance success/failure | Error preservation + success tracking |

#### Injection Strategies
1. **Periodic goal reminder**: Inject user goals every N turns
2. **Decision replay**: Re-surface key decisions before related work
3. **Error pattern review**: Summarize error patterns before similar tasks
4. **Tool rotation awareness**: Warn if single tool >80% of recent calls

#### Diversity Metrics
Track and alert on:
- **Tool entropy**: Shannon entropy of tool distribution
- **Topic coverage**: % of active goals addressed recently
- **Temporal balance**: Ratio of recent vs historical context
- **Outcome diversity**: Success/error/partial distribution

---

## Integration: How Techniques Work Together

```
┌────────────────────────────────────────────────────────────┐
│                    AGENT LOOP                              │
├────────────────────────────────────────────────────────────┤
│ 1. MONITOR (Technique 4) → Check thresholds                │
├────────────────────────────────────────────────────────────┤
│ 2. ATTENTION (Technique 5) → Recite todo.md                │
├────────────────────────────────────────────────────────────┤
│ 3. DIVERSITY (Technique 6) → Check diversity metrics       │
├────────────────────────────────────────────────────────────┤
│ 4. KV-CACHE (Technique 1) → Validate context structure     │
├────────────────────────────────────────────────────────────┤
│ 5. TOOL MASKING (Technique 2) → Bias tool selection        │
├────────────────────────────────────────────────────────────┤
│ 6. EXECUTE → Agent step                                    │
├────────────────────────────────────────────────────────────┤
│ 7. REDUCTION (Technique 4) → Compact/Summarize if needed   │
├────────────────────────────────────────────────────────────┤
│ 8. OFFLOAD (Technique 3) → Filesystem for cold context     │
└────────────────────────────────────────────────────────────┘
```

---

## Configuration Philosophy

**Defaults are opinionated but overridable:**
- Thresholds based on model context windows
- Strategies chosen per platform (OpenCode vs Generic)
- Weights tuned for typical coding agents
- All parameters tunable via `.agent_context_config.json`

**No magic numbers without rationale:**
- Every threshold has documented reasoning
- Every weight has empirical basis
- Every default has platform-specific variant