#!/bin/bash
set -euo pipefail

MODE="${1:-agent}"
CONFIG_FILE="${2:-.code-quality.yml}"

ERRORS=0

run_typecheck() {
    echo "🔍 TypeScript: Type checking..."
    if bun run typecheck > /tmp/cq_ts_typecheck.out 2>&1; then
        echo "✅ TypeScript typecheck passed"
    else
        echo "❌ TypeScript typecheck failed:"
        cat /tmp/cq_ts_typecheck.out
        ERRORS=1
    fi
}

run_lint() {
    echo "🔍 TypeScript: Linting..."
    if bun run lint > /tmp/cq_ts_lint.out 2>&1; then
        echo "✅ TypeScript lint passed"
    else
        echo "❌ TypeScript lint failed:"
        cat /tmp/cq_ts_lint.out
        ERRORS=1
    fi
}

run_format() {
    if [ "$MODE" = "ci" ]; then
        echo "🔍 TypeScript: Format check..."
        if bun run format:check > /tmp/cq_ts_format.out 2>&1; then
            echo "✅ TypeScript format check passed"
        else
            echo "❌ TypeScript format check failed:"
            cat /tmp/cq_ts_format.out
            ERRORS=1
        fi
    else
        echo "🔧 TypeScript: Format write..."
        if bun run format:write > /tmp/cq_ts_format.out 2>&1; then
            echo "✅ TypeScript format write completed"
        else
            echo "❌ TypeScript format write failed:"
            cat /tmp/cq_ts_format.out
            ERRORS=1
        fi
    fi
}

run_typecheck
run_lint
run_format

exit $ERRORS