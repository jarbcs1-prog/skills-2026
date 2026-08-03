# File Offloading Patterns — Complete Reference

This document provides comprehensive patterns for offloading context to filesystem with perfect restoration.

---

## Restorable Compression Rules

### 1. Web Content → Drop HTML, Keep URL
**Pattern:** When offloading web-fetched content, discard HTML/markdown, preserve canonical URL + metadata.

```json
{
  "type": "web_content",
  "url": "https://example.com/article",
  "title": "Article Title",
  "summary": "Key points extracted...",
  "fetched_at": "2026-08-03T10:00:00Z",
  "content_hash": "sha256:..."
}
```

**Restoration:** Re-fetch URL if needed (respect robots.txt, rate limits).

---

### 2. Document Content → Drop Text, Keep File Path
**Pattern:** For large documents (PDF, DOCX, XLSX), drop extracted text, keep file reference.

```json
{
  "type": "document",
  "file_path": "/workspace/docs/spec.pdf",
  "title": "API Specification v2.1",
  "pages": 45,
  "key_sections": ["Authentication", "Rate Limits", "Error Codes"],
  "content_hash": "sha256:..."
}
```

**Restoration:** Re-read file from path (supports local, S3, GCS via fsspec).

---

### 3. Tool Outputs → Drop Verbose, Keep Structured Result
**Pattern:** Tools often produce verbose logs. Keep structured output, offload full logs.

```json
{
  "type": "tool_call",
  "tool": "run_tests",
  "arguments": {"path": "tests/"},
  "structured_result": {"passed": 42, "failed": 0, "duration_ms": 1234},
  "verbose_output_offloaded": true,
  "offload_ref": {"path": ".agent_context/tool_outputs_0-10.jsonl.gz", "tokens": 15420}
}
```

**Restoration:** Load offload file for full logs when debugging.

---

### 4. Always Preserve (Never Drop)
| Element | Reason |
|---------|--------|
| **URLs** | Direct web access, canonical references |
| **File paths** | Local/remote document access |
| **IDs** (UUID, DB keys) | Unambiguous entity resolution |
| **Structured data** | Schema-dependent, hard to reconstruct |
| **Error messages** | Critical for debugging, often unique |
| **Timestamps** (ISO8601) | Temporal ordering, debugging |
| **User goals/constraints** | Intent preservation |

---

## Offloading Mechanisms

### Compression
| Algorithm | Ratio | Speed | Use Case |
|-----------|-------|-------|----------|
| **gzip** | 3-5x | Fast | Default, universal support |
| **zstd** | 4-6x | Fast | High-throughput, modern |
| **lz4** | 2-3x | Very fast | Real-time streaming |

**Default:** gzip (universal, good balance).

### Indexing (JSONL Index)
```jsonl
{"path":".agent_context/tool_calls_0-25.jsonl.gz","url":"file:///abs/path","tokens":45231,"sha256":"abc123...","metadata":{"type":"tool_calls","range":"0-25","summary":"Initial research","timestamp":"2026-08-03T10:00:00Z","platform":"generic"}}
{"path":".agent_context/tool_calls_26-50.jsonl.gz","url":"file:///abs/path","tokens":38912,"sha256":"def456...","metadata":{"type":"tool_calls","range":"26-50","summary":"Implementation phase","timestamp":"2026-08-03T10:05:00Z","platform":"generic"}}
```

**Benefits:**
- O(1) lookup by line number
- Streamable, no parsing full index
- Human-readable, diffable
- Metadata enables filtering/querying

### Versioning
```json
{
  "offload_version": 2,
  "schema_version": "1.0",
  "compatible_versions": ["1.0", "1.1"],
  "migration_path": "scripts/migrate_offload_v1_to_v2.py"
}
```

**Version Policy:**
- Semantic versioning for offload format
- Backward compatibility within major version
- Migration scripts provided for breaking changes
- Version embedded in every offload file

---

## Integration with Agent Workflow

### Automatic Offloading
Triggered by context monitor at thresholds:

```python
async def agent_step(context_history):
    status = monitor.check_context(estimate_tokens(context_history))
    
    if status.action == "compact":
        compacted, offloaded = compactor.compact(context_history)
        ref = offloader.offload(offloaded, metadata={"phase": "compaction"})
        context_history = compacted + [{"type": "context_reference", "ref": ref}]
    
    elif status.action == "summarize":
        summary = summarizer.summarize(context_history[:-3])
        ref = offloader.offload(context_history[:-3], metadata={"phase": "summarization"})
        context_history = [{"type": "summary", "data": summary}, {"type": "context_reference", "ref": ref}] + context_history[-3:]
```

### On-Demand Restoration
```python
# Agent explicitly requests restoration
def restore_context_segment(ref_path: str) -> List[Dict]:
    return offloader.restore(ref_path)

# Selective restoration by type/range
def restore_tool_calls(range_str: str) -> List[Dict]:
    refs = offloader.list_offloads(type_filter="tool_calls")
    # Filter by range, restore
```

### Reference Management
Context references are concise but informative:

```json
{
  "type": "context_reference",
  "ref": {
    "path": ".agent_context/tool_calls_0-25.jsonl.gz",
    "url": "file:///workspace/.agent_context/tool_calls_0-25.jsonl.gz",
    "tokens": 45231,
    "sha256": "abc123def456...",
    "metadata": {
      "type": "tool_calls",
      "range": "0-25",
      "summary": "Initial research phase"
    }
  }
}
```

Agent can decide to restore based on `summary`, `tokens`, `type`.

---

## Directory Structure

```
.agent_context/                    # or .opencode_context for OpenCode
├── index.jsonl                    # Master index (JSONL)
├── tool_calls_0-25.jsonl.gz
├── tool_calls_26-50.jsonl.gz
├── context_segment_50-100.jsonl.gz
├── summarization_20260803_100000.json.gz
└── compaction_20260803_100500.jsonl.gz
```

**Naming Convention:** `{type}_{range}_{timestamp}.{ext}`

---

## Cleanup & Maintenance

### Retention Policies
| Policy | Config | Default |
|--------|--------|---------|
| Max offload files | `cleanup_old(keep_recent=N)` | 100 |
| Max total tokens | `max_total_tokens` | 10M |
| Max age | `max_age_days` | 30 |
| Auto-cleanup | `auto_cleanup_enabled` | true |

### Cleanup Operation
```python
# Keep only 100 most recent offloads
removed = offloader.cleanup_old(keep_recent=100)

# Or cleanup by age
removed = offloader.cleanup_older_than(days=30)
```

---

## Integrity & Security

### Integrity Verification
Every offload includes SHA256:
```python
def restore(self, path: str) -> Any:
    data = self._read_compressed(path)
    if self._sha256(data) != index_entry["sha256"]:
        raise ValueError("Integrity check failed: data corrupted or tampered")
    return data
```

### Access Control
- **Local filesystem**: OS permissions
- **Remote storage**: IAM policies, signed URLs
- **Encryption**: Optional AES-256 at rest (`encryption: "aes256"` in config)

---

## Platform Differences

| Aspect | Generic | OpenCode |
|--------|---------|----------|
| Base path | `.agent_context` | `.opencode_context` |
| Offload triggers | Config thresholds | OpenCode hooks + config |
| Schema | Generic + OpenCode | OpenCode-optimized |
| Cleanup | Manual/auto | OpenCode lifecycle hooks |

---

## Troubleshooting

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| Restore fails SHA256 | Disk corruption / partial write | Re-offload from source, check disk health |
| Index missing entries | Index corruption | `offloader.rebuild_index()` |
| Offload path not found | Path moved / cleanup | Check retention policy, restore from backup |
| Compression error | Corrupted gzip | Delete file, re-offload |
| Out of disk space | Too many offloads | Run cleanup, increase `keep_recent` threshold |