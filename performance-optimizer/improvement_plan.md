# Improvement Plan: performance-optimizer

## Current State Assessment

**Tier:** 🟠 Functional but Thin (Needs Substantial Expansion)
**Lines:** 60 | **Version:** 1.0 (implied)

### Strengths
- Clear 6 analysis areas (algorithmic, database, memory, caching, async, network)
- Two-tier optimization strategies (quick wins vs major improvements)
- Structured output format with impact/effort/gain
- Mentions specific tools (Read, Grep, Bash)

### Gaps Identified
1. **No automated analysis** - Manual only, no profiling integration
2. **No language-specific rules** - Generic principles only
3. **No benchmarking framework** - No before/after measurement
4. **No CI integration** - Can't run in pipeline
5. **No performance regression detection** - No baseline tracking
6. **No resource-specific guidance** - CPU, memory, I/O, network
7. **No configuration** - Hardcoded analysis areas
8. **No report generation** - Only markdown output
9. **No integration with code-reviewer** - Separate workflow
10. **No examples or case studies**

---

## Improvement Roadmap

### Phase 1: Automation & Profiling (Week 1)
- [ ] Integrate with profiling tools (py-spy, perf, cProfile, node --inspect)
- [ ] Add language-specific analyzers (Python, JS/TS, Rust, Go, Java)
- [ ] Create automated bottleneck detection
- [ ] Build benchmarking harness

### Phase 2: Analysis Engine (Week 2)
- [ ] Implement rule engine for common patterns
- [ ] Add database query analysis (EXPLAIN plan parsing)
- [ ] Create memory leak detection patterns
- [ ] Add cache effectiveness analysis

### Phase 3: CI/CD & Regression (Week 3)
- [ ] Add GitHub Actions workflow for performance gates
- [ ] Implement baseline tracking with historical comparison
- [ ] Add performance budgets (max latency, memory, CPU)
- [ ] Create regression alerting

### Phase 4: Reporting & Integration (Week 4)
- [ ] Generate multiple report formats (HTML, JSON, SARIF, markdown)
- [ ] Integrate with `code-reviewer` (performance findings as review comments)
- [ ] Add `code-quality` integration (performance as quality gate)
- [ ] Create performance dashboard

---

## Specific Technical Tasks

### Profiling Integration
```python
# profiler.py
class Profiler:
    TOOLS = {
        "python": ["py-spy", "cProfile", "scalene", "memray"],
        "javascript": ["node --inspect", "0x", "clinic.js"],
        "rust": ["perf", "flamegraph", "cargo-profiler"],
        "go": ["pprof", "go tool trace"],
        "java": ["async-profiler", "JFR", "VisualVM"]
    }
    
    def profile(self, command: str, language: str, 
                duration: int = 30) -> ProfileResult:
        # Run appropriate profiler
        # Parse output into standardized format
        # Return: cpu_time, memory, allocations, call_graph
        pass
    
    def analyze_hotspots(self, profile: ProfileResult) -> List[Hotspot]:
        # Identify functions taking >5% CPU
        # Find allocation hotspots
        # Detect lock contention
        pass
```

### Rule Engine
```python
# rules.py
PERFORMANCE_RULES = {
    "python": [
        Rule("list-comprehension-vs-loop", "MEDIUM",
             pattern=r"for .* in .*:.*\.append\(",
             fix="Use list comprehension: [x for x in items]",
             gain="10-30% faster"),
        Rule("string-concatenation", "HIGH",
             pattern=r"\+.*str.*\+",
             fix="Use ''.join() or f-strings",
             gain="50-90% faster for many concatenations"),
        Rule("dict-get-vs-in", "LOW",
             pattern=r"if .* in .*:.*=.*\[.*\]",
             fix="Use dict.get(key, default)",
             gain="Cleaner, slightly faster"),
        Rule("generator-vs-list", "MEDIUM",
             pattern=r"\[.*for.*in.*\]",
             fix="Use generator (x for x in items) if not reusing",
             gain="Memory: O(1) vs O(n)"),
    ],
    "database": [
        Rule("n-plus-one", "CRITICAL",
             pattern=r"for .* in .*:.*\.query\(",
             fix="Use JOIN or batch loading (select_related, prefetch_related)",
             gain="100x+ faster for N items"),
        Rule("missing-index", "HIGH",
             pattern=r"WHERE .* = .*",
             fix="Add index on filtered column",
             gain="10-1000x faster"),
        Rule("select-star", "MEDIUM",
             pattern=r"SELECT \*",
             fix="Select only needed columns",
             gain="Less I/O, memory, network"),
    ],
    "javascript": [
        Rule("sync-in-loop", "HIGH",
             pattern=r"for.*await.*fetch",
             fix="Use Promise.all with map",
             gain="Parallel vs sequential"),
        Rule("large-bundle", "HIGH",
             pattern=r"import .* from ['\"]lodash",
             fix="Use lodash-es or tree-shaking imports",
             gain="Bundle size reduction"),
    ]
}
```

### Benchmarking Harness
```python
# benchmark.py
class BenchmarkHarness:
    def __init__(self, baseline_file: Path = Path(".perf_baseline.json")):
        self.baseline_file = baseline_file
        self.baselines = self.load_baselines()
    
    def run(self, benchmarks: List[Benchmark]) -> BenchmarkResult:
        results = []
        for bench in benchmarks:
            # Warmup
            for _ in range(3):
                bench.run()
            # Measure
            times = [bench.run() for _ in range(10)]
            results.append(BenchmarkMeasurement(
                name=bench.name,
                mean=statistics.mean(times),
                stdev=statistics.stdev(times) if len(times) > 1 else 0,
                min=min(times),
                max=max(times)
            ))
        return BenchmarkResult(results=results, timestamp=time.time())
    
    def compare(self, current: BenchmarkResult) -> RegressionReport:
        regressions = []
        improvements = []
        for curr in current.results:
            if curr.name in self.baselines:
                base = self.baselines[curr.name]
                change = (curr.mean - base.mean) / base.mean * 100
                if change > 10:  # 10% regression threshold
                    regressions.append(Regression(curr.name, change, base.mean, curr.mean))
                elif change < -5:  # 5% improvement threshold
                    improvements.append(Improvement(curr.name, change, base.mean, curr.mean))
        return RegressionReport(regressions=regressions, improvements=improvements)
```

### CLI Design
```bash
# performance-optimizer analyze --target src/ --language python --profile
# performance-optimizer benchmark --suite benchmarks/ --compare-baseline
# performance-optimizer profile --command "python app.py" --duration 60
# performance-optimizer report --input results.json --format html --output report.html
# performance-optimizer gate --budget latency=200ms,memory=500MB --ci
# performance-optimizer rules --language python --list
# performance-optimizer rules --add custom_rule.yaml
```

### CI Integration
```yaml
# .github/workflows/performance.yml
name: Performance Gate
on: [pull_request]
jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run benchmarks
        run: performance-optimizer benchmark --suite benchmarks/ --output current.json
      - name: Compare with baseline
        run: performance-optimizer compare --current current.json --baseline .perf_baseline.json --fail-on-regression
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: performance-report
          path: performance_report.html
```

---

## Acceptance Criteria
- [ ] Profilers integrate for 5+ languages
- [ ] Rule engine detects 50+ common patterns
- [ ] Benchmarking harness runs in CI <5 min
- [ ] Regression detection catches >90% of real regressions
- [ ] False positive rate <10%
- [ ] Reports generate in HTML, JSON, SARIF
- [ ] Integration with code-reviewer posts PR comments
- [ ] Performance budgets enforceable in CI

---

## Dependencies
- `code-reviewer` (performance findings as review comments)
- `code-quality` (performance as quality gate)
- `systematic-debugging` (root cause for complex issues)
- `verification-before-completion` (benchmark claims)
- `test-driven-development` (benchmark as test)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Profiler overhead | Medium | High | Sampling mode, configurable duration |
| False regressions | Medium | High | Statistical significance, multiple runs |
| Language coverage gaps | High | Medium | Community rules, plugin API |
| CI time increase | Medium | Medium | Parallel benchmarks, caching |

---

## Success Metrics
- Analysis coverage: 5+ languages, 50+ rules
- Regression detection: >90% recall, <10% false positive
- CI integration: <5 min added time
- User adoption: Used in >10 projects
- Performance improvements shipped: measurable gains