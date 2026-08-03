---
name: performance-optimizer
description: Use when performance issues are identified, code needs optimization, scalability concerns arise, or profiling analysis is needed. Analyzes code for performance bottlenecks across Python, JavaScript, Rust, Go, and Java.
version: "2.0.0"
---

# Performance Optimizer

Automated performance analysis, profiling integration, benchmarking harness, and regression detection across multiple languages.

## When to Use

- Performance issues identified in code
- Need to optimize slow code
- Scalability concerns
- Profiling analysis needed
- Setting performance budgets in CI
- Detecting performance regressions

## CLI Usage

```bash
# Analyze code for performance bottlenecks
performance-optimizer analyze --target src/ --language python --profile

# Run benchmarks and compare with baseline
performance-optimizer benchmark --suite benchmarks/ --compare-baseline

# Profile a command
performance-optimizer profile --command "python app.py" --duration 60

# Generate performance report
performance-optimizer report --input results.json --format html --output report.html

# Enforce performance budgets in CI
performance-optimizer gate --budget latency=200ms,memory=500MB --ci

# List available rules for a language
performance-optimizer rules --language python --list

# Add a custom rule
performance-optimizer rules --add custom_rule.yaml
```

## Supported Languages

| Language | Profilers | Rule Categories |
|----------|-----------|----------------|
| Python | py-spy, cProfile, scalene, memray | Algorithmic, string ops, generators, N+1 queries |
| JavaScript | node --inspect, 0x, clinic.js | Sync-in-loop, bundle size, async patterns |
| Rust | perf, flamegraph, cargo-profiler | Memory, allocations, lock contention |
| Go | pprof, go tool trace | Goroutine leaks, allocations, I/O |
| Java | async-profiler, JFR, VisualVM | GC pressure, thread contention, memory |

## Analysis Areas

1. **Algorithmic Complexity**: O(n), O(log n), O(1) analysis
2. **Database Queries**: N+1 problems, missing indexes
3. **Memory Usage**: Leaks, excessive allocation
4. **Caching**: Where to add caching
5. **Async**: Blocking vs non-blocking operations
6. **Network**: Request batching, compression

## Benchmarking

The benchmarking harness:
- Runs warmup iterations (3x) before measurement
- Takes 10 measurement samples per benchmark
- Computes mean, stdev, min, max
- Compares against baseline with regression threshold (10%)
- Detects improvements (5% threshold)

## CI Integration

```yaml
# .github/workflows/performance.yml
- name: Run performance benchmarks
  run: performance-optimizer benchmark --suite benchmarks/ --output current.json
- name: Compare with baseline
  run: performance-optimizer compare --current current.json --baseline .perf_baseline.json --fail-on-regression
```

## Architecture

```
CLI (scripts/cli.py)
  ├── analyze → rules.py (language-specific rules)
  ├── benchmark → benchmark.py (harness + baseline comparison)
  ├── profile → profiler.py (multi-language profiler integration)
  └── report → HTML/JSON/SARIF output formats
```

## Testing

```bash
pytest tests/ -v
```

27 tests covering CLI commands, benchmarking, profiling, and rule detection.
