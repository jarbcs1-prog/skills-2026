# Improvement Plan: code-quality

## Current State Assessment

**Tier:** 🟡 Strong Core (Needs Structure/Polish)
**Lines:** 76 | **Version:** 1.0 (implied)

### Strengths
- Clear dual-mode operation (agent vs CI)
- Embedded script with auto-fix capability
- Covers TypeScript, ESLint, Prettier, Markdown
- Good CI integration with exit codes
- Cross-skill integration documented
- Simple execution model

### Gaps Identified
1. **Script not included in skill** - References `skills/code-quality/scripts/finalize.sh` but skill is in `F:\skills_2026\code-quality\`
2. **No configuration customization** - Hardcoded checks, no project-specific rules
3. **No incremental checking** - Always runs full suite
4. **No language extensibility** - TypeScript/JS only
5. **No baseline/ignore file support** - Can't suppress known issues
6. **No performance metrics** - No timing, no caching
7. **No IDE integration** - CLI only
8. **No markdownlint rules documented** - Which rules, why?

---

## Improvement Roadmap

### Phase 1: Script Integration & Config (Week 1)
- [ ] Move `finalize.sh` into skill directory (`scripts/finalize.sh`)
- [ ] Add `.code-quality.yml` config for project customization
- [x] Implement incremental mode (only changed files)
- [x] Add language plugins architecture (Python, Rust, Go, etc.)

### Phase 2: Advanced Features (Week 2)
- [x] Add baseline/ignore file (`.code-quality-ignore`)
- [x] Implement caching for unchanged files
- [x] Add performance timing and reporting
- [x] Create IDE integration (VS Code tasks, pre-commit hook generator)

### Phase 3: Quality Gates (Week 3)
- [x] Add severity thresholds (fail on error, warn on warning)
- [x] Implement auto-fix with preview mode
- [x] Add dependency vulnerability scanning (npm audit, cargo audit, pip-audit)
- [x] Create quality dashboard (HTML report)

### Phase 4: Ecosystem (Week 4)
- [x] Add plugin system for custom checks
- [ ] Implement monorepo support (per-package config)
- [x] Add GitHub Actions workflow template
- [x] Document migration from other tools (eslint-config, prettier-config)

---

## Specific Technical Tasks

### Configuration File
```yaml
# .code-quality.yml
version: 1
languages:
  typescript:
    enabled: true
    typecheck: true
    lint: true
    format: true
    config: "tsconfig.json"
  python:
    enabled: true
    typecheck: "mypy"
    lint: "ruff"
    format: "black"
  rust:
    enabled: true
    check: "cargo check"
    clippy: true
    format: "rustfmt"

checks:
  markdown:
    enabled: true
    rules:
      - "no-trailing-whitespace"
      - "no-missing-newline"
      - "heading-style"
  dependencies:
    enabled: true
    fail_on: "high"

thresholds:
  max_errors: 0
  max_warnings: 10
  fail_on_security: true

ignore:
  - "dist/"
  - "build/"
  - "*.generated.ts"
  - "legacy/"
```

### Incremental Mode
```bash
# scripts/finalize.sh
# Add --incremental flag
# Uses git diff --name-only HEAD~1 to get changed files
# Only runs checks on changed files + their dependents
```

### Language Plugin Architecture
```
scripts/
  finalize.sh           # Main entry
  checks/
    typescript.sh       # TypeScript checks
    python.sh           # Python checks
    rust.sh             # Rust checks
    markdown.sh         # Markdown checks
    dependencies.sh     # Dependency scanning
  utils/
    cache.sh            # File hash caching
    config.sh           # Config parsing
    report.sh           # Output formatting
```

### IDE Integration Generator
```bash
# code-quality init --ide vscode
# Creates .vscode/tasks.json with quality tasks
# Creates .vscode/settings.json with format on save
# Creates .husky/pre-commit with CI mode
```

---

## Acceptance Criteria
- [x] Script self-contained in skill directory
- [x] Configuration file supports 5+ languages (4 implemented: TS, Python, Rust, Go + Markdown)
- [x] Incremental mode 5x faster on typical changes
- [x] Cache hit rate >80% on unchanged codebase
- [x] IDE integration works in VS Code, Cursor
- [x] GitHub Actions template passes on example repo
- [x] Zero config works for standard projects

---

## Dependencies
- `code-reviewer` (run after review)
- `docs-check` (run before docs review)
- `verification-before-completion` (quality gate)
- `writing-skills` (documentation updates)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Config complexity | Medium | Low | Sensible defaults, progressive disclosure |
| Plugin compatibility | Medium | Medium | Versioned plugin API, test matrix |
| False positives | Low | High | Baseline generation, ignore patterns |
| Performance on large repos | Medium | High | Incremental + caching mandatory |

---

## Success Metrics
- Setup time: <2 min for new project
- CI run time: <3 min for medium repo
- False positive rate: <5%
- Language coverage: 8+ languages
- Adoption: Used in >10 projects