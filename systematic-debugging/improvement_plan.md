# Improvement Plan: systematic-debugging

## Current State Assessment

**Tier:** 🟢 Production-Ready (Minor Polish)
**Lines:** 359 | **Version:** 1.0 (implied)

### Strengths
- Clear 4-phase process with Iron Law (no fixes without root cause)
- Detailed Phase 1 with 5 investigation steps (errors, reproduce, changes, evidence, trace)
- Phase 2 pattern analysis (working examples, references, differences, dependencies)
- Phase 3 scientific method (hypothesis, minimal test, verify, rule of three)
- Phase 4 implementation (regression test, single fix, verify, architecture questioning)
- Red flags table (20+ specific stop signals)
- Common rationalizations table (8 excuses vs reality)
- Quick reference table
- AI Agent integration with delegate_task template
- TDD integration for bug fixes
- Real-world impact metrics

### Gaps Identified
1. **No automated tooling** - Manual process only
2. **No debugging templates** - No structured worksheets
3. **No evidence management** - No systematic logging
4. **No hypothesis tracking** - Can't review failed hypotheses
5. **No collaboration features** - Single debugger only
6. **No integration with profiling** - Manual only
7. **No debugging patterns library** - No common bug patterns
8. **No metrics dashboard** - No debugging effectiveness tracking
9. **No CLI tooling** - Can't run as command
10. **No language-specific guidance** - Generic only

---

## Improvement Roadmap

### Phase 1: Templates & Worksheets (Week 1)
- [ ] Create debugging worksheet template (Phase 1-4 structured)
- [ ] Build hypothesis tracker (log hypotheses, tests, results)
- [ ] Add evidence log template (structured logging)
- [ ] Create debugging checklist per language

### Phase 2: Automation (Week 2)
- [ ] Build CLI for debugging workflow
- [ ] Integrate with profiling tools (py-spy, perf, cProfile)
- [ ] Add automated evidence gathering (logs, stack traces, state)
- [ ] Implement hypothesis testing harness

### Phase 3: Intelligence (Week 3)
- [ ] Build common bug pattern library (50+ patterns)
- [ ] Add root cause classification taxonomy
- [ ] Implement debugging analytics (time, success rate, patterns)
- [ ] Create debugging knowledge base

### Phase 4: Collaboration & Integration (Week 4)
- [ ] Add pair debugging mode
- [ ] Integrate with `code-reviewer` (debugging as review)
- [ ] Add CI/CD integration (failed test → debug workflow)
- [ ] Build debugging dashboard

---

## Specific Technical Tasks

### Debugging Worksheet
```markdown
# debugging-worksheet.md
## Phase 1: Root Cause Investigation

### Error Analysis
- **Error message**: [Paste full error]
- **Stack trace**: [Full trace with line numbers]
- **Error code**: [If applicable]
- **File:line**: [Primary location]

### Reproduction
- **Steps to reproduce**: [Numbered list]
- **Consistency**: [Always / Sometimes / Rare]
- **Environment**: [OS, Python version, deps]
- **Test command**: [Exact command that fails]

### Recent Changes
- **Git log (last 10)**: [Paste]
- **Uncommitted changes**: [Git diff summary]
- **Config changes**: [Any .env, config file changes]
- **Dependency changes**: [New/updated packages]

### Evidence Gathering
| Component | Input | Output | Expected | Actual | Status |
|-----------|-------|--------|----------|--------|--------|
| [name]    | [data] | [data] | [data]   | [data] | ✅/❌  |

### Data Flow Trace
- **Bad value origin**: [Variable/function]
- **Call chain**: [func1 → func2 → func3]
- **Source location**: [File:line where bad value created]

### Root Cause Hypothesis
- **Hypothesis**: [I think X because Y]
- **Confidence**: [High/Medium/Low]
- **Test plan**: [Minimal test to verify]

---

## Phase 2: Pattern Analysis
- **Working example found**: [File:line]
- **Reference implementation**: [Link/file]
- **Key differences**: [List]
- **Dependencies verified**: [Config, env, services]

---

## Phase 3: Hypothesis Testing
| # | Hypothesis | Test | Result | Next |
|---|------------|------|--------|------|
| 1 | [description] | [minimal change] | ✅/❌ | [Next hypothesis or Phase 4] |
| 2 | | | | |
| 3 | | | | |

**Rule of Three Check**: [ ] < 3 attempts → continue | [ ] ≥ 3 → Question architecture

---

## Phase 4: Implementation
- **Regression test**: [Test name, location]
- **Root cause fix**: [Single change description]
- **Verification**: [Test command, result]
- **Full suite**: [All tests pass?]

---

## Architecture Review (if 3+ fixes failed)
- **Pattern fundamentally sound?**: [Yes/No]
- **Shared state/coupling issues?**: [List]
- **Refactor vs continue?**: [Decision]
- **User discussion needed?**: [Yes/No]
```

### CLI Design
```bash
# systematic-debugging start --error "error message" --test "pytest test_x.py"
# systematic-debugging worksheet --output debug.md
# systematic-debugging evidence --component api --input "request" --output "response"
# systematic-debugging trace --variable "user_id" --from "main.py:10"
# systematic-debugging hypothesis --add "null pointer in auth" --test "mock auth"
# systematic-debugging pattern --search "similar bug" --language python
# systematic-debugging report --format html --output debug-report.html
```

### Bug Pattern Library
```python
# patterns.py
BUG_PATTERNS = {
    "null_pointer": {
        "symptoms": ["AttributeError: NoneType", "TypeError: None", "NullPointerException"],
        "common_causes": ["missing null check", "uninitialized variable", "failed lookup"],
        "investigation": ["trace variable assignment", "check all code paths", "verify initialization"],
        "fix_patterns": ["early return", "optional chaining", "default values", "assertion"]
    },
    "off_by_one": {
        "symptoms": ["IndexError", "missing last element", "extra iteration"],
        "common_causes": ["<= vs <", "range(len) vs range(len-1)", "0-index vs 1-index"],
        "investigation": ["check loop bounds", "verify array length", "trace index values"],
        "fix_patterns": ["boundary tests", "iterator instead of index", "assertions"]
    },
    "race_condition": {
        "symptoms": ["intermittent failures", "corrupted data", "deadlock"],
        "common_causes": ["shared mutable state", "non-atomic operations", "missing locks"],
        "investigation": ["add thread IDs to logs", "stress test", "check synchronization"],
        "fix_patterns": ["thread-local storage", "locks", "atomic operations", "immutable data"]
    },
    "memory_leak": {
        "symptoms": ["growing memory", "OOM kills", "slow degradation"],
        "common_causes": ["unclosed resources", "circular references", "cache without eviction"],
        "investigation": ["memory profiler", "object count tracking", "GC analysis"],
        "fix_patterns": ["context managers", "weak references", "cache TTL", "explicit cleanup"]
    },
    # ... 50+ patterns
}
```

### Debugging Analytics
```python
# analytics.py
class DebuggingAnalytics:
    def record_session(self, session: DebugSession):
        # Track: time_to_root_cause, hypotheses_tested, fixes_attempted
        # Pattern matched, success, new_bugs_introduced
        pass
    
    def get_effectiveness(self) -> EffectivenessReport:
        return EffectivenessReport(
            avg_time_to_root_cause=...,
            first_fix_success_rate=...,
            rule_of_three_trigger_rate=...,
            pattern_match_rate=...,
            regression_rate=...
        )
    
    def get_pattern_effectiveness(self) -> Dict[str, PatternStats]:
        # Which patterns lead to fastest resolution
        # Which patterns have highest recurrence
        pass
```

---

## Acceptance Criteria
- [ ] Worksheet template covers all 4 phases
- [ ] CLI guides through complete debugging session
- [ ] Pattern library has 50+ entries with >80% match rate
- [ ] Analytics track >10 metrics per session
- [ ] Integration with profiling tools works
- [ ] Pair debugging mode supports 2 debuggers
- [ ] Dashboard shows debugging effectiveness trends

---

## Dependencies
- `code-reviewer` (debugging as review)
- `systematic-debugging` (self - for CI integration)
- `test-driven-development` (regression test creation)
- `code-quality` (CLI code)
- `verification-before-completion` (effectiveness claims)
- `writing-skills` (documentation)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Worksheet overhead | Medium | Low | Optional, progressive disclosure |
| Pattern misclassification | Medium | Medium | Confidence scoring, human override |
| Analytics privacy | Low | High | Local-only, opt-in sharing |

---

## Success Metrics
- Time to root cause: <15 min avg (vs 30+ min manual)
- First-fix success rate: >90% (vs 40% guessing)
- Rule of three triggers: <5% of sessions
- Pattern library coverage: >80% of bugs matched
- Debugging session documentation: 100% structured