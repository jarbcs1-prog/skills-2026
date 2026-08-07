---
name: code-quality
description: "Run comprehensive code quality checks across multiple languages (TypeScript, Python, Rust, Go) including type checking, linting, formatting, markdown validation, and dependency scanning. Supports incremental mode (only changed files), configuration via .code-quality.yml, and auto-fix capabilities. Use when: (1) Before committing code changes, (2) In CI/CD pipelines for automated quality gates, (3) After making significant code changes, (4) When preparing code for review, (5) When ensuring code meets quality standards, (6) For type checking, linting, formatting and markdown validation, (7) In pre-commit hooks or (8) For automated quality gates before merging. Triggers: finalize, code quality, typecheck, lint, format, check code, quality check, run checks, pre-commit, before commit, CI checks, validate code."
---

# Code Quality

Run comprehensive code quality checks across multiple languages: TypeScript, Python, Rust, Go, Markdown validation, and dependency scanning.

## Scripts

Scripts are embedded in this skill directory. Two entry points are available:

### Shell Script
```bash
# From the skill root directory:
bash scripts/finalize.sh ci       # CI mode (read-only checks)
bash scripts/finalize.sh agent    # Agent mode (auto-fixes formatting)
bash scripts/finalize.sh ci .code-quality.yml  # With custom config
```

### Python CLI
```bash
# From the skill root directory:
python -m scripts.cli finalize --mode ci        # CI mode
python -m scripts.cli finalize --mode agent     # Agent mode (auto-fix)
python -m scripts.cli init --ide vscode         # Generate IDE integration
python -m scripts.cli config show               # Show effective config
python -m scripts.cli config validate           # Validate config
python -m scripts.cli incremental --language python  # List changed files
```

## Configuration

Create a `.code-quality.yml` file at your project root to customize checks. If no config file is found, sensible defaults are used (all languages enabled, incremental mode on).

```yaml
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
  go:
    enabled: true
    vet: true
    lint: "golangci-lint"
    format: "gofmt"

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
  - "node_modules/"
  - ".next/"

incremental:
  enabled: true
  base: "HEAD~1"
  cache: true

reporting:
  format: "text"
  output: null
```

## Architecture

```
scripts/
  finalize.sh              # Main entry point (shell)
  cli.py                   # CLI entry point (Python)
  incremental.py           # Git-based changed file detection
  quality_config.py        # YAML config loading and validation
  __init__.py              # Package marker
  checks/
    typescript.sh          # TypeScript (bun, ESLint, Prettier)
    python.sh              # Python (ruff, mypy, black)
    rust.sh                # Rust (cargo check, clippy, rustfmt)
    go.sh                  # Go (go vet, golangci-lint, gofmt)
    markdown.sh            # Markdown quality checks
    dependencies.sh        # Dependency vulnerability scanning (npm audit, cargo audit, pip-audit)
  utils/
    cache.sh               # File hash caching, incremental file detection
    config.sh              # YAML config parsing for shell scripts
    report.sh              # Output formatting (text/json)
```

## Checks Performed

### TypeScript
1. **Type Checking** - `bun run typecheck`
2. **ESLint Linting** - `bun run lint`
3. **Prettier Formatting** - `bun run format:check` (CI) / `bun run format:write` (agent)

### Python
1. **Ruff Linting** - `ruff check .`
2. **mypy Type Checking** - `mypy .`
3. **Black Formatting** - `black --check .` (CI) / `black .` (agent)

### Rust
1. **cargo check** - Type and compilation checks
2. **Clippy** - Linting with warnings as errors
3. **rustfmt** - Formatting check/write

### Go
1. **go vet** - Static analysis
2. **golangci-lint** - Linting
3. **gofmt** - Formatting

### Markdown
1. Trailing whitespace detection
2. Missing newline at end of file
3. Heading style consistency

### Dependencies
1. npm audit (Node.js projects)
2. cargo audit (Rust projects)
3. pip-audit (Python projects)

## Modes

### Agent Mode (`agent`)
- Auto-fixes formatting issues (Prettier, Black, gofmt, rustfmt)
- Reports type/lint errors for manual fixing
- Exits with code 1 if any check fails

### CI Mode (`ci`)
- Read-only: no auto-fixes
- Fails on type errors, lint errors, and formatting violations
- Exits with code 0 (pass) or 1 (fail) for CI pipelines

## Incremental Mode

When enabled in `.code-quality.yml` (`incremental.enabled: true`), only files changed since the configured base revision (default: `HEAD~1`) are checked. This provides significant speedups on large codebases.

File hashing is cached in `~/.cache/code-quality/file_hashes.txt` to avoid re-checking unchanged files across runs.

## Workflow

### Running Quality Checks

1. **Choose mode**:
   - Agent mode: `bash scripts/finalize.sh agent` - Auto-fixes formatting while checking for type and lint errors
   - CI mode: `bash scripts/finalize.sh ci` - Read-only checks for CI pipelines

2. **Review results**: Check terminal output for errors and warnings
   - TypeScript errors show file paths and line numbers
   - ESLint/Pyright warnings include rule names and suggestions
   - Formatter issues are auto-fixed in agent mode
   - Markdown issues show file paths and line numbers

3. **Fix issues**: Address any errors that weren't auto-fixed
   - Type errors: Fix type mismatches, missing types or incorrect imports
   - Lint errors: Follow linter suggestions or disable rules with comments
   - Markdown issues: Fix trailing whitespace or add missing newlines

4. **Re-run checks**: Execute the same command again to verify all issues are resolved

### IDE Integration

Generate IDE integration files:
```bash
python -m scripts.cli init --ide vscode
```

This creates:
- `.vscode/tasks.json` - VS Code tasks for running code quality checks
- `.vscode/settings.json` - Format-on-save settings
- `.husky/pre-commit` - Pre-commit hook with incremental mode

### GitHub Actions

A CI workflow template is provided at `.github/workflows/ci.yml`. It runs on push/PR and executes all quality checks in CI mode.

## Integration

- Run after **code-reviewer** skill to ensure reviewed code meets quality standards
- Run before **docs-check** skill to ensure code is clean before documentation review
- Use in CI pipelines as a quality gate before merging PRs

## References

- `references/documentation-guide.md` - Documentation standards

## Output

Terminal output. Exits with code 0 (pass) or 1 (fail) for CI pipelines.
