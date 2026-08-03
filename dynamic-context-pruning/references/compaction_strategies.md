# Compaction Strategies — Complete Reference

This document details all **8 compaction strategies** implemented in the Dynamic Context Pruning Skill, covering both Generic (4) and OpenCode-specific (4) modes.

---

## Generic Strategies (Platform-Agnostic)

### 1. Token Budget Allocation (`token_budget`)

**Concept:** Allocate a fixed token budget across history segments proportionally.

**Algorithm:**
1. Calculate total tokens in context
2. Set budget = total × (1 - compact_ratio)
3. Reserve tokens for `keep_recent_full` recent entries
4. Fill remaining budget from oldest entries forward
5. Offload entries exceeding budget

**Parameters:**
- `compact_ratio`: Fraction to reduce (default 0.5 = 50%)
- `keep_recent_full`: Recent entries preserved fully (default 5)
- `preserve_structure`: Keep tool call/response structure (default true)

**Use Case:** Predictable token reduction when context exceeds threshold.

---

### 2. Age-Based Compaction (`age_based`)

**Concept:** Compact oldest N% of context entries, preserving recent history.

**Algorithm:**
1. Calculate `num_to_compact = len(context) × compact_ratio`
2. Protect `keep_recent_full` most recent entries
3. Offload entries from index 0 to `len - num_to_compact - protected`
3. Compacted context = protected recent + middle (uncompacted)

**Parameters:**
- `compact_ratio`: Fraction of entries to offload (default 0.5)
- `keep_recent_full`: Recent entries fully preserved (default 5)

**Use Case:** Simple, predictable reduction when temporal relevance is primary factor.

---

### 3. Importance-Based Compaction (`importance_based`)

**Concept:** Score each entry by relevance, compact lowest-scored entries.

**Scoring Weights (default):**
| Entry Type | Weight | Rationale |
|------------|--------|-----------|
| `user_goals` | 1.0 | Directly reflects user intent |
| `errors` | 0.9 | Critical for debugging |
| `key_decisions` | 0.8 | Architectural importance |
| `tool_outputs` | 0.5 | Structured but verbose |
| `intermediate_steps` | 0.3 | Often redundant |

**Algorithm:**
1. Score each entry based on `type` field and weights
2. Sort by score ascending (least important first)
3. Protect `keep_recent_full` recent entries
4. Offload lowest-scored entries up to `compact_ratio`

**Use Case:** Preserves semantically important context when token reduction needed.

---

### 4. Hybrid Compaction (`hybrid`) — **Default**

**Concept:** Combines age-based (70%) and importance-based (30%) strategies.

**Algorithm:**
1. Run both AgeBasedCompactor and ImportanceBasedCompactor
2. Union of entries marked for offloading by either strategy
3. Preserve original ordering in compacted result

**Rationale:** Age captures temporal relevance; importance captures semantic relevance. Union ensures both dimensions are respected.

**Use Case:** Best general-purpose strategy when no platform-specific optimization available.

---

## OpenCode-Specific Strategies

### 5. Timestamp Hiding (`timestamp_hiding`) — **OpenCode Default**

**Concept:** OpenCode's native non-destructive timestamp-based message hiding. Marks old entries as hidden rather than removing them.

**Algorithm:**
1. Keep last `keep_recent_full` entries fully visible
2. For older entries: add `"_hidden": true` and `"_hidden_reason": "timestamp_hiding"`
3. Offload full original data to filesystem
4. Compacted context includes hidden markers + recent full entries

**Restoration:** Replaces hidden entries with full offloaded data.

**Advantages:**
- Non-destructive (full history preserved offloaded)
- Native OpenCode compatibility
- Instant toggle between compacted/full views

**Use Case:** OpenCode agents needing reversible compaction with full fidelity restoration.

---

### 6. Head/Tail Protection (`head_tail_protection`)

**Concept:** Token budgeting per tool output, preserving critical head (context) and tail (result/errors), pruning verbose middle.

**Algorithm:**
1. For each tool call with output > `max_tool_output_tokens`:
   - Keep first `max_tool_output_tokens × 2` chars (head)
   - Keep last `max_tool_output_tokens × 2` chars (tail)
   - Replace middle with `"\n... [pruned] ...\n"`
   - Mark entry with `"_pruned": true` and `"_original_length"`
2. Offload full original output to filesystem

**Parameters:**
- `max_tool_output_tokens`: Budget per tool output (default 8192)

**Use Case:** Tool outputs often have verbose middle sections (logs, stack traces) with critical info at start/end.

---

### 7. Repeated Tool Pruning (`repeated_tool_pruning`)

**Concept:** Identify repeated tool calls (same tool + same arguments), keep only most recent output.

**Algorithm:**
1. Group tool calls by `tool_name + JSON(arguments)` key
2. For groups with >1 call: mark all but most recent as hidden
3. Add `"_hidden": true` and `"_hidden_reason": "repeated_tool_pruning"`
4. Offload hidden entries to filesystem

**Use Case:** Eliminates redundancy from retry loops, polling, or repeated file reads.

---

### 8. Error Preservation (`error_preservation`)

**Concept:** Prune errored tool call inputs after N turns, but always preserve error messages and surrounding context.

**Algorithm:**
1. Track indices of tool calls with errors
2. Keep context within `error_turns_to_keep` (default 3) of errors
3. For older tool calls: prune `"input"` field (replace with `"[pruned]"`), mark `"_input_pruned": true`
4. Always preserve error messages and stack traces
5. Offload pruned inputs to filesystem

**Parameters:**
- `error_turns_to_keep`: Context window around errors (default 3)

**Use Case:** Debugging — errors and surrounding context are critical, but old successful inputs are noise.

---

## Strategy Selection Guide

| Scenario | Recommended Strategy |
|----------|---------------------|
| Generic agent, simple reduction | `hybrid` (default) |
| Predictable token budget | `token_budget` |
| Temporal relevance primary | `age_based` |
| Semantic importance varies | `importance_based` |
| **OpenCode agent** | `timestamp_hiding` |
| **OpenCode + verbose tools** | `head_tail_protection` |
| **OpenCode + retry loops** | `repeated_tool_pruning` |
| **OpenCode + debugging** | `error_preservation` |

---

## Configuration Reference

```json
{
  "compaction": {
    "strategy": "hybrid|token_budget|age_based|importance_based|timestamp_hiding|head_tail_protection|repeated_tool_pruning|error_preservation",
    "keep_recent_full": 5,
    "compact_ratio": 0.5,
    "preserve_structure": true,
    "protect_zones": ["head", "tail"],
    "max_tool_output_tokens": 8192,
    "importance_weights": {
      "user_goals": 1.0,
      "errors": 0.9,
      "key_decisions": 0.8,
      "tool_outputs": 0.5,
      "intermediate_steps": 0.3
    }
  }
}
```

---

## Reversibility Guarantees

All strategies implement **lossless restoration** via offloaded data:

1. **Offload:** Full original entries saved to compressed JSONL files
2. **Reference:** Compacted context includes `context_reference` with file path, SHA256, token count
3. **Restore:** `compactor.restore(compacted, offload_path)` → original context
3. **Verification:** SHA256 checksum validates integrity

**Test Coverage:** All 8 strategies tested for 100% reversibility in `test_compaction_reversibility.py`.