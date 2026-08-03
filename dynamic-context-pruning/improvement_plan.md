# Improvement Plan: dynamic-context-pruning

## Current State Assessment

**Tier:** 🟢 Production-Ready (Minor Polish)
**Lines:** 350 | **Version:** 1.0.0

### Strengths
- Comprehensive 6-workflow architecture (monitor, compact, summarize, offload, kv-cache, integration)
- Clear progressive disclosure levels
- Python class-based implementation with config-driven setup
- Restorable compression principles well-defined
- KV-cache optimization rules
- Integration example for agent loops
- References to detailed documentation
- Testing commands documented

### Gaps Identified
1. **Scripts not included** - References `scripts/*.py` but skill dir has no scripts/
2. **References not included** - References 5 reference files but not present
3. **Examples not included** - References `examples/` directory but not present
4. **No CLI entry points** - Only Python API, no command-line interface
5. **No token estimation** - No `estimate_tokens()` implementation
6. **No schema validation** - Config file not validated
7. **No metrics/telemetry** - Can't measure effectiveness
8. **No OpenCode-specific adaptation** - Generic, not integrated with OpenCode hooks
9. **No compression format versioning** - Offloaded files lack version
10. **No recovery testing** - Restore not validated in CI

---

## Improvement Roadmap

### Phase 1: Core Implementation (Week 1)
- [ ] Create all 5 script modules with full implementations
- [ ] Write 5 reference documents
- [ ] Create `examples/` with basic and full agent loops
- [ ] Add CLI entry points for all workflows

### Phase 2: Quality & Validation (Week 2)
- [ ] Add config schema validation (JSON Schema)
- [ ] Implement token estimation (tiktoken integration)
- [ ] Add compression format versioning with migration
- [ ] Create comprehensive test suite (unit + integration)

### Phase 3: OpenCode Integration (Week 3)
- [ ] Add OpenCode hook integration (auto-trigger on context thresholds)
- [ ] Create OpenCode-specific config presets
- [ ] Add context inspection commands for OpenCode UI
- [ ] Implement agent-loop integration patterns

### Phase 4: Observability (Week 4)
- [ ] Add metrics collection (compaction ratio, summary quality, offload size)
- [ ] Create context health dashboard
- [ ] Add alerting for threshold breaches
- [ ] Implement A/B testing for compaction strategies

---

## Specific Technical Tasks

### Script Implementations
```python
# scripts/context_monitor.py
class ContextMonitor:
    def __init__(self, config: ContextConfig):
        self.thresholds = config.thresholds
        self.history = []
    
    def check_context(self, tokens: int) -> ContextStatus:
        # Returns action: none|compact|summarize|critical
        pass
    
    def get_metrics(self) -> ContextMetrics:
        # Returns: tokens_used, percent, trend, predicted_exhaustion
        pass

# scripts/compaction.py
class Compactor:
    def compact(self, context: List[ContextEntry]) -> Tuple[List[ContextEntry], OffloadedData]:
        # Implements: token_budget, age_based, importance_based, hybrid
        pass
    
    def restore(self, compacted: List[ContextEntry], offload_path: str) -> List[ContextEntry]:
        pass

# scripts/summarization.py
class Summarizer:
    def __init__(self, schema: SummarySchema, model: str):
        self.schema = schema
        self.model = model
    
    def summarize(self, context: List[ContextEntry]) -> StructuredSummary:
        # Uses structured output, not free-form
        pass
    
    def validate(self, summary: StructuredSummary, original: List[ContextEntry]) -> ValidationResult:
        pass

# scripts/file_offloader.py
class FileOffloader:
    def offload(self, data: Any, metadata: OffloadMetadata) -> OffloadReference:
        # Compresses, writes, returns reference with path, url, tokens
        pass
    
    def restore(self, path: str) -> Any:
        pass

# scripts/kv_cache.py
class KVCacheOptimizer:
    def validate(self, context: List[ContextEntry]) -> List[CacheIssue]:
        # Checks: stable prefix, append-only, deterministic JSON, cache breakpoints
        pass
    
    def fix(self, context: List[ContextEntry]) -> List[ContextEntry]:
        pass
```

### CLI Entry Points
```bash
# dynamic-context-pruning monitor --config .agent_context_config.json
# dynamic-context-pruning compact --context history.json --output compacted.json
# dynamic-context-pruning summarize --context history.json --schema agent_default
# dynamic-context-pruning offload --data context_segment.json --metadata meta.json
# dynamic-context-pruning kv-cache --validate --fix --context history.json
# dynamic-context-pruning thresholds --show --update --config .agent_context_config.json
```

### Config Schema
```json
# .agent_context_config.schema.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "thresholds": { "type": "object", "required": ["hard_limit", "pre_rot_threshold", "compaction_trigger", "summarization_trigger"] },
    "compaction": { "type": "object", "properties": { "strategy": {"enum": ["token_budget", "age_based", "importance_based", "hybrid"]} } },
    "summarization": { "type": "object" },
    "offloading": { "type": "object" },
    "kv_cache": { "type": "object" }
  },
  "required": ["thresholds", "compaction", "summarization", "offloading", "kv_cache"]
}
```

### Token Estimation
```python
# scripts/token_estimator.py
import tiktoken

def estimate_tokens(text: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def estimate_context_tokens(context: List[ContextEntry]) -> int:
    total = 0
    for entry in context:
        total += estimate_tokens(json.dumps(entry, sort_keys=True))
    return total
```

---

## Acceptance Criteria
- [ ] All 5 scripts implemented and tested
- [ ] 5 reference documents complete
- [ ] CLI works for all 5 workflows
- [ ] Config schema validates all options
- [ ] Token estimation accurate within 5%
- [ ] Compaction reversibility 100% (lossless restore)
- [ ] Summarization schema validation catches 100% of invalid summaries
- [ ] KV-cache optimizer fixes 100% of detected issues
- [ ] Offloading/restore roundtrip preserves all data
- [ ] Integration examples run without errors

---

## Dependencies
- `opencode/dynamic-context-pruning` (OpenCode-specific variant - merge candidate)
- `code-quality` (script validation)
- `test-driven-development` (test approach)
- `verification-before-completion` (quality claims)
- `writing-skills` (reference documentation)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Script complexity | Medium | High | Modular classes, clear interfaces |
| Token estimation variance | Medium | Medium | Model-specific encodings, calibration |
| Restore failures | Low | Critical | Roundtrip tests, format versioning |
| Performance overhead | Low | Medium | Lazy imports, caching |

---

## Success Metrics
- Context reduction: >60% token savings at summarization trigger
- Compaction speed: <100ms for 100K tokens
- Summarization quality: >0.85 schema compliance
- Restore success: 100%
- KV-cache issues: 0 in production
- Integration adoption: Used by >5 agent implementations