# Improvement Plan: test-driven-development

## Current State Assessment

**Tier:** 🟢 Production-Ready (Minor Polish)
**Lines:** 335 | **Version:** 1.0 (implied)

### Strengths
- Clear Iron Law (NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST)
- Detailed RED-GREEN-REFACTOR cycle with examples
- Good vs bad test examples
- Mandatory verification steps
- Common rationalizations table (13 excuses vs reality)
- Red flags checklist (13 stop signals)
- Verification checklist (9 items)
- When stuck guidance (4 problems → solutions)
- Hermes Agent integration (terminal commands, delegate_task template)
- Testing anti-patterns (4 patterns)
- Final rule summary

### Gaps Identified
1. **No CLI tooling** - Manual TDD enforcement only
2. **No IDE integration** - No VS Code/Cursor integration
3. **No language-specific guidance** - Python only (pytest)
4. **No test generation** - No scaffolding for new tests
5. **No coverage enforcement** - No minimum coverage gates
6. **No mutation testing** - No test quality validation
7. **No TDD metrics** - No tracking of TDD adherence
8. **No pair TDD support** - Solo only
9. **No legacy code strategies** - Greenfield only
10. **No integration with code-reviewer** - Separate workflow

---

## Improvement Roadmap

### Phase 1: CLI & Automation (Week 1)
- [ ] Create TDD CLI (`tdd` command)
- [ ] Add test scaffolding (`tdd new --feature "retry logic"`)
- [ ] Implement RED-GREEN-REFACTOR enforcement
- [ ] Add pre-commit hook for TDD verification

### Phase 2: Language Support & Quality (Week 2)
- [ ] Add language configs (Python/pytest, JS/Jest, Rust/cargo test, Go/testing, Java/JUnit)
- [ ] Integrate coverage enforcement (min 80%)
- [ ] Add mutation testing (mutmut, stryker)
- [ ] Create test quality linter

### Phase 3: Metrics & Integration (Week 3)
- [ ] Build TDD adherence tracker
- [ ] Integrate with `code-reviewer` (TDD as review criterion)
- [ ] Add `systematic-debugging` integration (bug → test first)
- [ ] Create TDD dashboard

### Phase 4: Advanced Features (Week 4)
- [ ] Legacy code TDD strategies (characterization tests)
- [ ] Pair TDD mode (driver/navigator)
- [ ] Test-first refactoring workflow
- [ ] TDD coaching/training mode

---

## Specific Technical Tasks

### CLI Design
```bash
# tdd new --feature "user authentication" --language python
# tdd red --test "tests/test_auth.py::test_login_fails_with_wrong_password"
# tdd green --implement "src/auth.py"
# tdd refactor --clean "src/auth.py"
# tdd cycle --auto "tests/test_auth.py" "src/auth.py"
# tdd verify --coverage 80 --mutation
# tdd coach --mode strict --language python
# tdd stats --project . --period 30d
```

### TDD Enforcer
```python
# enforcer.py
class TDDEnforcer:
    def __init__(self, config: TDDConfig):
        self.config = config
        self.state = CycleState.RED
    
    def check_test_first(self, test_file: Path, source_file: Path) -> EnforcementResult:
        # 1. Check test file modified before source
        # 2. Verify test fails initially (git diff + run)
        # 3. Verify minimal implementation
        # 4. Verify refactor doesn't add behavior
        pass
    
    def verify_red(self, test_command: str) -> bool:
        # Run test, confirm it fails for expected reason
        result = subprocess.run(test_command, capture_output=True)
        return result.returncode != 0 and "FAILED" in result.stdout
    
    def verify_green(self, test_command: str) -> bool:
        # Run test, confirm it passes
        result = subprocess.run(test_command, capture_output=True)
        return result.returncode == 0
    
    def verify_refactor(self, test_command: str, coverage_threshold: float) -> bool:
        # Run full suite, check coverage, no new behavior
        pass
```

### Language Configurations
```yaml
# languages.yaml
python:
  test_framework: pytest
  test_command: "pytest {test_file} -v"
  coverage_command: "pytest --cov={source} --cov-fail-under=80"
  mutation_command: "mutmut run --paths-to-mutate {source}"
  test_naming: "test_*.py"
  test_pattern: "def test_.*:"

javascript:
  test_framework: jest
  test_command: "jest {test_file} --verbose"
  coverage_command: "jest --coverage --coverageThreshold='{\"global\":{\"statements\":80}}'"
  mutation_command: "stryker run"
  test_naming: "*.test.js"
  test_pattern: "test\\(|it\\("

rust:
  test_framework: cargo
  test_command: "cargo test {test_name} -- --nocapture"
  coverage_command: "cargo tarpaulin --fail-under 80"
  mutation_command: "cargo mutate"
  test_naming: "#[test]"
  test_pattern: "#\\[test\\]"

go:
  test_framework: go test
  test_command: "go test -v -run {test_name} ./..."
  coverage_command: "go test -coverprofile=coverage.out && go tool cover -func=coverage.out"
  mutation_command: "go-mutesting"
  test_naming: "*_test.go"
  test_pattern: "func Test.*\\("
```

### Pre-commit Hook
```bash
# .git/hooks/pre-commit
#!/bin/bash
# TDD Enforcement Hook

# Check if test files changed without source changes (RED phase)
# Check if source files changed without test changes (should have tests)
# Run affected tests to verify GREEN

CHANGED_FILES=$(git diff --cached --name-only)
TEST_FILES=$(echo "$CHANGED_FILES" | grep -E "(test_|_test\.|\\.test\.)" || true)
SOURCE_FILES=$(echo "$CHANGED_FILES" | grep -vE "(test_|_test\.|\\.test\.)" || true)

if [ -n "$SOURCE_FILES" ] && [ -z "$TEST_FILES" ]; then
    echo "❌ TDD VIOLATION: Source files changed without test changes"
    echo "   Files: $SOURCE_FILES"
    echo "   Write failing test first (RED phase)"
    exit 1
fi

# Run tests for changed files
if [ -n "$TEST_FILES" ]; then
    # Run specific tests
    pytest $TEST_FILES -v
    if [ $? -ne 0 ]; then
        echo "❌ Tests failing - fix implementation (GREEN phase)"
        exit 1
    fi
fi
```

---

## Acceptance Criteria
- [ ] CLI enforces RED-GREEN-REFACTOR cycle
- [ ] Supports 5+ languages with native test frameworks
- [ ] Coverage gate at 80% enforced
- [ ] Mutation testing integrated
- [ ] Pre-commit hook catches TDD violations
- [ ] TDD dashboard shows adherence metrics
- [ ] Legacy code strategies documented
- [ ] Pair TDD mode functional

---

## Dependencies
- `code-quality` (CLI validation)
- `systematic-debugging` (bug → test first)
- `code-reviewer` (TDD as review criterion)
- `verification-before-completion` (enforcement claims)
- `writing-skills` (documentation)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Developer resistance | High | High | Coaching mode, gradual adoption |
| False positives | Medium | Medium | Configurable strictness |
| Language coverage gaps | Medium | Low | Plugin architecture for test frameworks |
| Performance overhead | Low | Medium | Incremental test running |

---

## Success Metrics
- TDD adherence: >90% of commits follow cycle
- Test coverage: >80% maintained
- Mutation score: >70%
- Pre-commit violations: <5% of commits
- Bug regression rate: <5%
- Developer satisfaction: >4/5