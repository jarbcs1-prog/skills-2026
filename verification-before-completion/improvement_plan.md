# Improvement Plan: verification-before-completion

## Current State Assessment

**Tier:** 🟢 Production-Ready (Minor Polish)
**Lines:** 139 | **Version:** 1.0 (implied)

### Strengths
- Clear Iron Law (NO COMPLETION CLAIM WITHOUT FRESH VERIFICATION EVIDENCE)
- The Gate Function (5-step mandatory process)
- Common failures table (7 claim types with required vs insufficient)
- Red flags (8 stop signals)
- Rationalization prevention table (9 excuses vs reality)
- Key patterns for tests, regression, build, requirements, agent delegation
- 24 failure memories with consequences
- Clear when-to-apply (ALWAYS before success claims)
- Rule applies to exact phrases, paraphrases, synonyms, implications

### Gaps Identified
1. **No automated verification CLI** - Manual process only
2. **No IDE integration** - No pre-commit/pre-push hooks
3. **No verification templates** - No standardized checklists per project type
4. **No CI/CD integration** - No pipeline gates
5. **No verification history** - Can't track verification effectiveness
6. **No agent verification** - Can't verify subagent claims automatically
7. **No partial verification handling** - No guidance on incremental verification
8. **No team/shared verification** - Solo only
9. **No metrics/dashboard** - No verification compliance tracking
10. **No exception handling** - No guidance for emergency overrides

---

## Improvement Roadmap

### Phase 1: Automation & Templates (Week 1)
- [x] Create verification CLI (`verify` command)
- [x] Build project-type verification templates (5 types: Python, Rust, JS, Go, Generic)
- [x] Add pre-commit/pre-push hooks
- [x] Create verification checklist generator (requirements command)

### Phase 2: CI/CD & Integration (Week 2)
- [x] Add GitHub Actions/GitLab CI verification gates
- [x] Integrate with `code-quality` (verification as quality gate)
- [x] Add TDD verification (test command with expected result)
- [x] Create agent verification wrapper (AgentVerifier)

### Phase 3: Intelligence & Tracking (Week 3)
- [x] Build verification history/logging (history.jsonl)
- [x] Add compliance dashboard (ComplianceReport)
- [x] Implement verification analytics (false completion rate, avg time)
- [x] Create team verification workflows (shared state dir)

### Phase 4: Advanced Features (Week 4)
- [x] Add emergency override with audit trail
- [x] Build verification coaching mode (strict/guided/permissive)
- [x] Add cross-project verification standards (project type detection)
- [ ] Create verification certification

---

## Specific Technical Tasks

### Verification CLI
```bash
# verify tests --command "pytest tests/ -q" --expect "pass"
# verify build --command "cargo build --release" --expect "exit 0"
# verify linter --command "ruff check ." --expect "0 errors"
# verify requirements --checklist requirements.md --all
# verify agent --task "implement feature" --agent-output output.log
# verify all --project . --gate
# verify history --period 30d --stats
# verify coach --mode strict
```

### Verification Templates
```python
# templates.py
VERIFICATION_TEMPLATES = {
    "python": {
        "tests": "pytest tests/ -q",
        "lint": "ruff check . && mypy .",
        "build": "python -m py_compile src/**/*.py",
        "typecheck": "mypy --strict .",
        "security": "bandit -r .",
    },
    "rust": {
        "tests": "cargo test --all",
        "lint": "cargo clippy -- -D warnings",
        "build": "cargo build --release",
        "fmt": "cargo fmt --check",
        "audit": "cargo audit",
    },
    "javascript": {
        "tests": "jest --ci",
        "lint": "eslint . --ext .js,.ts,.tsx",
        "build": "tsc --noEmit",
        "format": "prettier --check .",
        "audit": "npm audit",
    },
    "go": {
        "tests": "go test ./...",
        "lint": "golangci-lint run",
        "build": "go build ./...",
        "vet": "go vet ./...",
    },
    "generic": {
        "requirements": "checklist.md",
        "tests": "run-tests.sh",
        "build": "build.sh",
        "deploy": "deploy.sh --dry-run",
    }
}

def get_verification_commands(project_type: str, phase: str) -> List[VerificationStep]:
    # Return ordered verification steps for project type and phase
    # Phase: pre-commit, pre-push, pre-deploy, post-deploy
    pass
```

### Pre-commit Hook
```bash
# .git/hooks/pre-commit
#!/bin/bash
# Verification Before Completion - Pre-commit Hook

# 1. Check for completion claims in commit message
COMMIT_MSG=$(cat $1)
if echo "$COMMIT_MSG" | grep -qiE "(done|complete|fixed|finished|ready|working)"; then
    echo "⚠️  Commit message suggests completion. Running verification..."
    
    # Run project verification
    if [ -f "verify.yaml" ]; then
        verify all --config verify.yaml --gate
        if [ $? -ne 0 ]; then
            echo "❌ Verification failed. Commit blocked."
            echo "   Fix issues or use 'git commit --no-verify' for emergency."
            exit 1
        fi
    else
        # Default verification based on project detection
        if [ -f "Cargo.toml" ]; then
            cargo test --quiet && cargo clippy -- -D warnings && cargo fmt --check
        elif [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
            pytest -q && ruff check . && mypy .
        elif [ -f "package.json" ]; then
            npm test && npm run lint
        elif [ -f "go.mod" ]; then
            go test ./... && golangci-lint run
        fi
        
        if [ $? -ne 0 ]; then
            echo "❌ Verification failed. Commit blocked."
            exit 1
        fi
    fi
    
    echo "✅ Verification passed."
fi
```

### Agent Verification Wrapper
```python
# agent_verify.py
class AgentVerifier:
    def __init__(self, verifier: 'VerificationCLI'):
        self.verifier = verifier
    
    def verify_agent_task(self, task: AgentTask, result: AgentResult) -> VerificationResult:
        # 1. Check VCS diff matches claimed changes
        claimed_files = result.claimed_files
        actual_diff = self.get_vcs_diff()
        if not self.files_match(claimed_files, actual_diff):
            return VerificationResult(
                passed=False,
                reason="VCS diff doesn't match claimed changes",
                evidence={"claimed": claimed_files, "actual": actual_diff}
            )
        
        # 2. Run project verification
        verification = self.verifier.verify_all()
        
        # 3. Check specific task requirements
        task_verification = self.verify_task_requirements(task, result)
        
        return VerificationResult(
            passed=verification.passed and task_verification.passed,
            details={...}
        )
    
    def verify_task_requirements(self, task: AgentTask, result: AgentResult) -> TaskVerification:
        # Parse task for specific requirements
        # e.g., "add tests for X" → run tests for X
        # e.g., "fix bug Y" → run reproduction test for Y
        pass
```

### Verification Dashboard
```python
# dashboard.py
class VerificationDashboard:
    def get_compliance_report(self, period: Period) -> ComplianceReport:
        return ComplianceReport(
            total_verifications=...,
            passed_rate=...,
            false_completion_rate=...,
            avg_verification_time=...,
            most_common_failures=...,
            agent_verification_rate=...,
            emergency_overrides=...
        )
    
    def get_team_metrics(self) -> TeamMetrics:
        return TeamMetrics(
            per_member_compliance=...,
            verification_culture_score=...,
            improvement_trend=...
        )
```

---

## Acceptance Criteria
- [x] CLI runs verification in <30s for typical project
- [x] Templates cover 5 languages/project types
- [x] Pre-commit hook blocks false completions
- [x] Agent verification catches false claims (VCS diff check)
- [x] Dashboard shows real-time compliance
- [x] Emergency override requires audit trail
- [x] Integration with CI/CD passes verification as gate

---

## Dependencies
- `code-quality` (verification commands)
- `test-driven-development` (TDD cycle verification)
- `systematic-debugging` (bug fix verification)
- `code-reviewer` (review as verification)
- `verification-before-completion` (self)
- `writing-skills` (documentation)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Verification fatigue | High | Medium | Smart defaults, incremental verification |
| False positives | Medium | High | Configurable strictness, escape hatches |
| Emergency bypass abuse | Low | Critical | Audit trail, approval required |
| Tool complexity | Medium | Low | Progressive disclosure, good defaults |

---

## Success Metrics
- False completion rate: <2% (from ~20%)
- Verification time: <30s avg
- Compliance rate: >95%
- Agent verification adoption: >80% of delegations
- Emergency overrides: <1/month
- Team satisfaction: >4/5