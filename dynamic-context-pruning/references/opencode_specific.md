# OpenCode-Specific Context Engineering

This document details OpenCode-specific context engineering techniques integrated into the unified Dynamic Context Pruning Skill.

---

## OpenCode Architecture Overview

OpenCode has unique context management features that differ from generic agents:

| Feature | Description |
|---------|-------------|
| **Prompt Cache** | Persistent KV-cache across turns |
| **Native Compaction** | Timestamp-based message hiding |
| **Hook System** | Pre/post turn hooks for context management |
| **Tool Streaming** | Real-time tool output streaming |
| **Session Management** | Built-in session persistence |

---

## OpenCode-Specific Thresholds

```json
{
  "thresholds": {
    "hard_limit": 200000,
    "pre_rot_threshold": 100000,
    "compaction_trigger": 150000,
    "summarization_trigger": 175000
  }
}
```

**Rationale:** OpenCode's standard model has 200K context window. Pre-rot at 100K (50%) where attention degradation begins.

---

## OpenCode Compaction Strategies

### 1. Timestamp Hiding (Native)
OpenCode's built-in non-destructive compaction.

**Mechanism:**
- Marks messages older than threshold as hidden
- Adds `_hidden: true` and `_hidden_reason: "timestamp_hiding"`
- Preserves full history in offloaded data
- Instant toggle between compacted/full views

**Configuration:**
```json
{
  "opencode": {
    "compaction_strategy": "timestamp_hiding",
    "keep_recent_full": 5
  }
}
```

**Restoration:** Automatic — hidden messages restored from offload on demand.

---

### 2. Head/Tail Protection
Token budgeting per tool output.

**Problem:** Tool outputs often have verbose middle (logs, stack traces) with critical info at start/end.

**Solution:**
```
[HEAD - first 2000 tokens] ... [PRUNED] ... [TAIL - last 2000 tokens]
```

**Implementation:**
```python
def prune_tool_output(output: str, budget: int = 2000) -> dict:
    if len(output) <= budget * 2:
        return {"output": output, "_pruned": False}
    
    head = output[:budget]
    tail = output[-budget:]
    return {
        "output": head + "\n... [pruned] ...\n" + tail,
        "_pruned": True,
        "_original_length": len(output)
    }
```

**Configuration:**
```json
{
  "compaction": {
    "protect_zones": ["head", "tail"],
    "max_tool_output_tokens": 2000
  }
}
```

---

### 3. Repeated Tool Pruning
Eliminates redundancy from retry loops, polling, repeated reads.

**Detection:** Group by `tool_name + JSON(arguments)` key.

**Action:** Keep only most recent, hide others with `"_hidden_reason": "repeated_tool_pruning"`.

**Example:**
```json
{
  "type": "tool_call",
  "tool": "read_file",
  "arguments": {"path": "config.json"},
  "_hidden": true,
  "_hidden_reason": "repeated_tool_pruning",
  "_duplicate_of": 42
}
```

---

### 4. Error Preservation
Always preserve errors and surrounding context.

**Policy:**
- Always preserve error messages and stack traces
- Keep context within 3 turns of errors
- Prune inputs of older successful tool calls
- Mark pruned inputs: `"_input_pruned": true`

**Configuration:**
```json
{
  "opencode": {
    "error_preservation": true,
    "error_turns_to_keep": 3
  }
}
```

---

## OpenCode Summarization Schema (5-Heading)

OpenCode uses a standard 5-field summary format:

```json
{
  "fields": [
    "current_state",
    "completed_actions",
    "pending_actions",
    "key_decisions",
    "errors_encountered"
  ],
  "required": ["current_state", "pending_actions"]
}
```

**Field Mapping from Generic:**
| Generic Field | OpenCode Field | Notes |
|---------------|----------------|-------|
| `current_state` | `current_state` | Same |
| `user_goals` | (merged) | Part of current_state |
| `completed_actions` | `completed_actions` | New field |
| `pending_actions` | `pending_actions` | Same |
| `errors_encountered` | `errors_encountered` | Same |
| `key_decisions` | `key_decisions` | Same |
| `files_modified` | (omitted) | Tracked via git |

---

## OpenCode Integration Patterns

### Hook Integration
```bash
# Pre-turn hook: monitor context
opencode hook pre-turn --command "dynamic-context-pruning monitor"

# Post-turn hook: auto-compact if needed
opencode hook post-turn --command "dynamic-context-pruning auto-prune"
```

### Native Compaction Integration
```python
# Use OpenCode's native compaction when available
if opencode.has_native_compaction():
    opencode.compact(strategy="timestamp_hiding")
else:
    # Fallback to skill implementation
    compactor = OpenCodeCompactor(config)
    compacted, offloaded = compactor.compact(context)
```

### Session Management
```json
{
  "opencode_session": {
    "session_id": "abc123",
    "context_tokens": 145000,
    "last_compaction": "2026-08-03T10:00:00Z",
    "compaction_count": 3,
    "offload_dir": ".opencode_context"
  }
}
```

---

## OpenCode-Specific Configuration

### Complete OpenCode Config Section
```json
{
  "platform": "opencode",
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
    "schema": "opencode_5_heading",
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

---

## OpenCode CLI Commands

```bash
# Context monitoring
opencode-dynamic-context-pruning monitor

# Manual compaction
opencode-dynamic-context-pruning compact

# Manual summarization
opencode-dynamic-context-pruning summarize

# Offload context
opencode-dynamic-context-pruning offload

# Check thresholds
opencode-dynamic-context-pruning thresholds

# Platform management
opencode-dynamic-context-pruning platform --set opencode

# KV-cache validation
opencode-dynamic-context-pruning kv-cache --validate --fix
```

---

## OpenCode Context Monitor Integration

### Real-Time Monitoring
```python
class OpenCodeContextMonitor:
    def __init__(self, config_path=".opencode_context_config.json"):
        self.monitor = ContextMonitor.from_config(config_path)
    
    def on_turn_start(self, context):
        tokens = estimate_tokens(context)
        status = self.monitor.check_context(tokens)
        
        if status.action in ["compact", "summarize"]:
            # Trigger OpenCode hook
            opencode.emit("context_pruning_needed", {
                "action": status.action,
                "tokens": tokens,
                "percent": status.percent
            })
        
        return status
    
    def on_turn_end(self, context, action_taken):
        # Log metrics
        tokens = estimate_tokens(context)
        metrics = self.monitor.get_metrics()
        opencode.emit("context_metrics", {
            "tokens": tokens,
            "action": action_taken,
            "metrics": metrics
        })
```

---

## OpenCode-Specific Testing

```bash
# Test OpenCode compaction strategies
python scripts/test_opencode_strategies.py

# Test platform detection
python scripts/test_platform_detection.py

# Test native compaction integration
python scripts/test_native_compaction.py
```

### Test Cases
| Test | Description |
|------|-------------|
| `test_timestamp_hiding_reversibility` | Hidden messages restore perfectly |
| `test_head_tail_protection` | Tool outputs pruned correctly |
| `test_repeated_tool_pruning` | Duplicate tool calls detected |
| `test_error_preservation` | Errors and 3-turn context preserved |
| `test_opencode_schema_compliance` | 5-heading schema validation |
| `test_native_compaction_integration` | OpenCode hook triggers correctly |

---

## Migration from Generic to OpenCode

### Auto-Detection
```python
def detect_opencode():
    return any([
        os.environ.get("OPENCODE_SESSION_ID"),
        os.environ.get("AGENT_FRAMEWORK") == "opencode",
        Path(".opencode").exists(),
        Path(".opencode_context_config.json").exists(),
    ])
```

### Config Migration
```bash
# Generate OpenCode config
dynamic-context-pruning config --generate --platform opencode --output .opencode_context_config.json

# Or merge existing config with OpenCode defaults
dynamic-context-pruning config --merge --platform opencode
```

---

## OpenCode Performance Characteristics

| Metric | Generic | OpenCode |
|--------|---------|----------|
| Hard limit | 256K | 200K |
| Native compaction | No | Yes (timestamp hiding) |
| Prompt cache | External | Built-in |
| Compaction speed | ~50ms | ~20ms (native) |
| Restoration | File-based | File + native |
| Hook integration | Manual | Automatic |

---

## Best Practices for OpenCode

1. **Use native timestamp hiding** — fastest, most reliable
2. **Enable all 4 OpenCode strategies** — they complement each other
3. **Set `keep_recent_full=5`** — balances context retention with token savings
4. **Use `opencode_5_heading` schema** — matches OpenCode conventions
5. **Monitor via hooks** — integrates with OpenCode's event system
6. **Offload to `.opencode_context`** — keeps project clean
6. **Validate KV-cache every 10 turns** — prevents silent degradation

---

## Troubleshooting OpenCode Context Issues

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| Native compaction not triggering | Hook not registered | `opencode hook add pre-turn dynamic-context-pruning monitor` |
| Timestamp hiding not working | Old OpenCode version | Update OpenCode, or fallback to skill compaction |
| 5-heading schema validation fails | Wrong field names | Use `opencode_5_heading` schema exactly |
| Context not restoring | Offload path mismatch | Check `.opencode_context/` exists, rebuild index |
| KV-cache issues persist | Prefix not stable | Run `kv-cache --validate --fix` |

---

## OpenCode Context Engineering Checklist

- [ ] OpenCode config created with `platform: "opencode"`
- [ ] Native timestamp hiding enabled
- [ ] Head/tail protection for tool outputs
- [ ] Repeated tool pruning enabled
- [ ] Error preservation with 3-turn window
- [ ] 5-heading summarization schema
- [ ] Offloading to `.opencode_context/`
- [ ] KV-cache validation every 10 turns
- [ ] Pre-turn monitoring hook registered
- [ ] Post-turn metrics emission
- [ ] Native compaction integration tested
- [ ] Platform auto-detection verified