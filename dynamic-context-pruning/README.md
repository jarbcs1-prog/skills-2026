# Dynamic Context Pruning

Context engineering for long-horizon agents — reversible compaction, irreversible summarization, filesystem offloading, and KV-cache optimization.

## Quick Start

```bash
# Run tests
python -m pytest scripts/ -v

# Run benchmark
python scripts/benchmark_context_reduction.py

# Run individual tests
python scripts/test_compaction_reversibility.py
python scripts/test_summarization_schema.py
```

## Install

No external dependencies — uses Python 3.10+ stdlib only.

## What's Inside

### Scripts (`scripts/`)

| Script | Purpose |
|--------|---------|
| `compaction.py` | Reversible context reduction (drop content, keep references) |
| `context_monitor.py` | Threshold monitoring and transition alerts |
| `summarization.py` | Structured irreversible summarization |
| `file_offloader.py` | Filesystem offloading with restorable references |
| `kv_cache.py` | KV-cache validation and prefix fixing |
| `benchmark_context_reduction.py` | Measure token reduction ratios across strategies |
| `test_compaction_reversibility.py` | 11 tests: compact/restore identity, offload round-trips |
| `test_summarization_schema.py` | 19 tests: schema validation, type checking, edge cases |

### Examples (`examples/`)

- `basic_agent_loop.py` — Minimal integration example
- `full_agent_loop.py` — Complete agent loop with all features
- `config_examples/minimal.json` — Thresholds-only config
- `config_examples/full.json` — Complete config matching SKILL.md schema
- `config_examples/production.json` — Conservative production thresholds

### References (`references/`)

- `context_engineering_principles.md` — Six techniques deep dive
- `compaction_strategies.md` — Detailed compaction algorithms
- `summarization_schemas.md` — Structured summary schemas
- `kv_cache_optimization.md` — KV-cache friendly patterns
- `file_offloading_patterns.md` — Restorable compression rules
- `api_reference.md` — API reference for all modules

## Configuration

See `templates/config_template.json` or `examples/config_examples/` for config schemas.

## License

MIT
