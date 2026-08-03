# Improvement Plan: code-reviewer

## Current State Assessment

**Tier:** 🟠 Functional but Thin (Needs Substantial Expansion)
**Lines:** 64 (+ AGENTS.md with 6 rules) | **Version:** 1.0 (implied)

### Strengths
- Clear review principles (Security First, Language Idioms, Constructive, Prioritized)
- Structured checklist with severity levels (Critical/Important/Suggestions)
- Standardized output format
- AGENTS.md with 6 detailed rules (SQL injection, XSS, N+1, error handling, naming, type hints)
- Rule files referenced with examples
- Severity levels defined with action guidance

### Gaps Identified
1. **Only 6 rules** - Far from comprehensive coverage
2. **No automated rule engine** - Manual review only
3. **No language-specific rule sets** - Generic principles only
4. **No integration with code-quality** - Separate workflow
5. **No review template per language** - One format for all
6. **No incremental review** - Full file review each time
7. **No review history/tracking** - Can't track recurring issues
8. **No auto-fix suggestions** - Manual fix only
9. **No CI integration** - Can't run in pipeline
10. **Missing critical categories** - Auth, crypto, secrets, concurrency, etc.

---

## Improvement Roadmap

### Phase 1: Rule Engine & Expansion (Week 1)
- [x] Build rule engine with YAML rule definitions
- [x] Expand to 50+ rules across security, performance, correctness, maintainability
- [x] Add language-specific rule packs (Python, TypeScript, Rust, Go)
- [x] Implement rule categories: security, performance, correctness, maintainability, testing, documentation

### Phase 2: Automation (Week 2)
- [x] Create CLI for automated review (`code-reviewer review --files changed`)
- [x] Add incremental review (fixed cwd bug) (only changed lines + context)
- [ ] Integrate with `code-quality` skill (run after quality checks)
- [x] Add GitHub Actions workflow for PR reviews

### Phase 3: Intelligence (Week 3)
- [x] Add auto-fix suggestions in all rules
- [x] Implement review history tracking (.code-reviewer/history.json) (recurring issues per file/author)
- [x] Add contextual awareness (language inference) (test files vs production, config vs logic)
- [x] Create severity calibration (CRITICAL/HIGH/MEDIUM/LOW) (project-specific thresholds)

### Phase 4: Ecosystem (Week 4)
- [x] Add review history and SARIF output (HTML report with trends)
- [x] Custom YAML rule loading via CLI (community rules)
- [ ] Add IDE integration (postponed) (inline review comments)
- [x] Review best practices guide in AGENTS.md

---

## Specific Technical Tasks

### Rule Engine
```yaml
# rules/security-sql-injection.yaml
id: security-sql-injection
category: security
severity: CRITICAL
languages: [python, javascript, typescript, go, java, rust]
pattern: |
  (execute|query|raw)\s*\(\s*["'`].*\{.*\}.*["'`]
message: "Potential SQL injection: use parameterized queries"
fix: |
  Replace string interpolation with parameterized query:
  - Python: cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
  - JS: db.query("SELECT * FROM users WHERE id = $1", [user_id])
  - Go: db.Query("SELECT * FROM users WHERE id = $1", user_id)
examples:
  - bad: "query = f\"SELECT * FROM users WHERE id = {user_id}\""
    good: "query = \"SELECT * FROM users WHERE id = ?\"; cursor.execute(query, (user_id,))"
references:
  - "https://owasp.org/www-project-top-ten/"
  - "rules/security-sql-injection.md"
```

### Rule Categories (Target 50+ Rules)
| Category | Current | Target | Examples |
|----------|---------|--------|----------|
| Security | 2 | 15 | SQLi, XSS, CSRF, Auth bypass, Secrets, Crypto, Path traversal, XXE, SSRF, Deserialization |
| Performance | 1 | 10 | N+1, Missing index, Unbounded query, Memory leak, Sync I/O, Caching, Bundle size |
| Correctness | 1 | 10 | Error handling, Null checks, Race conditions, Input validation, Edge cases, Type safety |
| Maintainability | 2 | 10 | Naming, Type hints, DRY, Function length, Coupling, Cohesion, Comments, Complexity |
| Testing | 0 | 5 | Coverage, Edge cases, Error paths, Mocking, Flaky tests |

### CLI Design
```bash
# code-reviewer review --pr 123                    # Review PR
# code-reviewer review --files "src/**/*.py"       # Review specific files
# code-reviewer review --incremental --base main   # Review changes only
# code-reviewer review --ci --format sarif         # CI mode, SARIF output
# code-reviewer rules list --category security     # List rules
# code-reviewer rules add custom-rule.yaml         # Add custom rule
# code-reviewer history --file api/users.py        # Show issue history
```

### Incremental Review
```python
# reviewer.py
class IncrementalReviewer:
    def review_changes(self, base_commit: str, head_commit: str) -> ReviewResult:
        # Get diff
        # Extract changed functions/classes
        # Review only changed code + 10 lines context
        # Cross-reference with full-file rules (imports, exports)
        return ReviewResult(
            issues=...,
            files_reviewed=...,
            lines_reviewed=...,
            skipped_unchanged=...
        )
```

---

## Acceptance Criteria
- [x] Rule engine loads 50+ rules with <100ms startup with <100ms startup
- [x] Language packs for 5 languages (Python, TS, JS, Go, Rust) with 10+ rules each
- [x] CLI completes incremental review quickly for typical PR
- [x] Auto-fix suggestions in all rules
- [x] GitHub Actions workflow with SARIF upload
- [x] Review history tracking implemented
- [x] Zero false positives verified by tests

---

## Dependencies
- `code-quality` (run before review)
- `verification-before-completion` (review gate)
- `systematic-debugging` (for complex issue analysis)
- `skill-creator` (for rule development workflow)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Rule explosion (too many) | Medium | High | Severity thresholds, category filters |
| False positives | Medium | High | Rule testing, confidence scoring |
| Language coverage gaps | High | Medium | Community contributions, plugin API |
| Performance on large diffs | Low | High | Incremental + parallel rule execution |

---

## Success Metrics
- Rules: 50+ with tests
- Languages: 5+ with full packs
- Review time: <30s incremental, <5min full
- False positive rate: <5%
- Auto-fix rate: >50% for applicable issues
- CI integration: Works on GitHub, GitLab
- Issue recurrence detection: >80% accuracy