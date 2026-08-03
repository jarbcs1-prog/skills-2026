#!/bin/bash
set -euo pipefail

MODE="${1:-agent}"
CONFIG_FILE="${2:-.code-quality.yml}"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [ "$MODE" != "ci" ] && [ "$MODE" != "agent" ]; then
    echo "❌ Error: Invalid mode '$MODE'"
    echo "Usage: $0 [ci|agent] [config]"
    echo "  ci:    Runs format:check (read-only checks) - for CI/CD pipelines"
    echo "  agent: Runs format:write (auto-fixes formatting) - for agent sessions"
    echo "  config: Path to .code-quality.yml (default: .code-quality.yml)"
    exit 1
fi

ERRORS=0
CHECKS_PASSED=0
CHECKS_FAILED=0
TOTAL_FILES=0

source "$SKILL_DIR/scripts/utils/config.sh" "$CONFIG_FILE"
source "$SKILL_DIR/scripts/utils/cache.sh"

INCREMENTAL_BASE=$(get_incremental_base)
INCREMENTAL_ENABLED=$(get_incremental_enabled)

echo "🚀 Running code quality checks in $MODE mode..."
echo "📋 Config: $CONFIG_FILE"
if [ "$INCREMENTAL_ENABLED" = "true" ]; then
    echo "🔄 Incremental mode: base=$INCREMENTAL_BASE"
fi
echo ""

run_check() {
    local name="$1"
    local cmd="$2"
    local output_file="$3"

    echo "🔍 $name..."
    if eval "$cmd" > "$output_file" 2>&1; then
        echo "✅ $name passed"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo "❌ $name failed:"
        cat "$output_file"
        echo "❌ $name failed" >> "$output_file"
        ERRORS=1
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi
    echo ""
}

TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

# TypeScript checks
if [ "$(get_language_enabled typescript)" = "true" ]; then
    if [ "$INCREMENTAL_ENABLED" = "true" ]; then
        TS_FILES=$(changed_files "$INCREMENTAL_BASE" ".ts" ".tsx" ".js" ".jsx" 2>/dev/null || true)
        if [ -z "$TS_FILES" ]; then
            echo "⏭️  TypeScript: No changed files, skipping"
            echo ""
        else
            echo "📄 TypeScript: $TS_FILES changed file(s)"
            run_check "TypeScript typecheck" "bun run typecheck" "$TMPDIR/ts_typecheck.out"
            run_check "TypeScript lint" "bun run lint" "$TMPDIR/ts_lint.out"
            if [ "$MODE" = "ci" ]; then
                run_check "TypeScript format check" "bun run format:check" "$TMPDIR/ts_format.out"
            else
                run_check "TypeScript format write" "bun run format:write" "$TMPDIR/ts_format.out"
            fi
        fi
    else
        run_check "TypeScript typecheck" "bun run typecheck" "$TMPDIR/ts_typecheck.out"
        run_check "TypeScript lint" "bun run lint" "$TMPDIR/ts_lint.out"
        if [ "$MODE" = "ci" ]; then
            run_check "TypeScript format check" "bun run format:check" "$TMPDIR/ts_format.out"
        else
            run_check "TypeScript format write" "bun run format:write" "$TMPDIR/ts_format.out"
        fi
    fi
fi

# Python checks
if [ "$(get_language_enabled python)" = "true" ]; then
    if [ "$INCREMENTAL_ENABLED" = "true" ]; then
        PY_FILES=$(changed_files "$INCREMENTAL_BASE" ".py" 2>/dev/null || true)
        if [ -z "$PY_FILES" ]; then
            echo "⏭️  Python: No changed files, skipping"
            echo ""
        else
            echo "📄 Python: $PY_FILES changed file(s)"
            run_check "Python ruff lint" "ruff check ." "$TMPDIR/py_ruff.out"
            run_check "Python mypy" "mypy ." "$TMPDIR/py_mypy.out"
            if [ "$MODE" = "ci" ]; then
                run_check "Python format check" "black --check ." "$TMPDIR/py_black.out"
            else
                run_check "Python format write" "black ." "$TMPDIR/py_black.out"
            fi
        fi
    else
        run_check "Python ruff lint" "ruff check ." "$TMPDIR/py_ruff.out"
        run_check "Python mypy" "mypy ." "$TMPDIR/py_mypy.out"
        if [ "$MODE" = "ci" ]; then
            run_check "Python format check" "black --check ." "$TMPDIR/py_black.out"
        else
            run_check "Python format write" "black ." "$TMPDIR/py_black.out"
        fi
    fi
fi

# Rust checks
if [ "$(get_language_enabled rust)" = "true" ]; then
    if [ "$INCREMENTAL_ENABLED" = "true" ]; then
        RS_FILES=$(changed_files "$INCREMENTAL_BASE" ".rs" 2>/dev/null || true)
        if [ -z "$RS_FILES" ]; then
            echo "⏭️  Rust: No changed files, skipping"
            echo ""
        else
            echo "📄 Rust: $RS_FILES changed file(s)"
            run_check "Rust cargo check" "cargo check" "$TMPDIR/rs_check.out"
            run_check "Rust clippy" "cargo clippy -- -D warnings" "$TMPDIR/rs_clippy.out"
            if [ "$MODE" = "ci" ]; then
                run_check "Rust format check" "rustfmt --check ." "$TMPDIR/rs_fmt.out"
            else
                run_check "Rust format write" "rustfmt ." "$TMPDIR/rs_fmt.out"
            fi
        fi
    else
        run_check "Rust cargo check" "cargo check" "$TMPDIR/rs_check.out"
        run_check "Rust clippy" "cargo clippy -- -D warnings" "$TMPDIR/rs_clippy.out"
        if [ "$MODE" = "ci" ]; then
            run_check "Rust format check" "rustfmt --check ." "$TMPDIR/rs_fmt.out"
        else
            run_check "Rust format write" "rustfmt ." "$TMPDIR/rs_fmt.out"
        fi
    fi
fi

# Go checks
if [ "$(get_language_enabled go)" = "true" ]; then
    if [ "$INCREMENTAL_ENABLED" = "true" ]; then
        GO_FILES=$(changed_files "$INCREMENTAL_BASE" ".go" 2>/dev/null || true)
        if [ -z "$GO_FILES" ]; then
            echo "⏭️  Go: No changed files, skipping"
            echo ""
        else
            echo "📄 Go: $GO_FILES changed file(s)"
            run_check "Go vet" "go vet ./..." "$TMPDIR/go_vet.out"
            run_check "Go golangci-lint" "golangci-lint run" "$TMPDIR/go_lint.out"
            if [ "$MODE" = "ci" ]; then
                run_check "Go format check" "gofmt -l ." "$TMPDIR/go_fmt.out"
            else
                run_check "Go format write" "gofmt -w ." "$TMPDIR/go_fmt.out"
            fi
        fi
    else
        run_check "Go vet" "go vet ./..." "$TMPDIR/go_vet.out"
        run_check "Go golangci-lint" "golangci-lint run" "$TMPDIR/go_lint.out"
        if [ "$MODE" = "ci" ]; then
            run_check "Go format check" "gofmt -l ." "$TMPDIR/go_fmt.out"
        else
            run_check "Go format write" "gofmt -w ." "$TMPDIR/go_fmt.out"
        fi
    fi
fi

# Markdown checks
run_check "Markdown" "bash $SKILL_DIR/scripts/checks/markdown.sh $MODE $CONFIG_FILE" "$TMPDIR/md.out"

# Dependency checks
if [ "$(get_config_value checks.dependencies.enabled)" = "true" ]; then
    run_check "Dependencies" "bash $SKILL_DIR/scripts/checks/dependencies.sh $MODE $CONFIG_FILE" "$TMPDIR/dep.out"
fi

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Check Results:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Passed: $CHECKS_PASSED"
echo "Failed: $CHECKS_FAILED"
echo ""

if [ "$ERRORS" -eq 0 ]; then
    echo "✅ All checks passed!"
    exit 0
else
    echo "❌ Some checks failed. Please fix the errors above."
    exit 1
fi