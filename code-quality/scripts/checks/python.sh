#!/bin/bash
set -euo pipefail

MODE="${1:-agent}"
CONFIG_FILE="${2:-.code-quality.yml}"

ERRORS=0

run_ruff() {
    echo "🔍 Python: Ruff linting..."
    if ruff check . > /tmp/cq_py_ruff.out 2>&1; then
        echo "✅ Ruff lint passed"
    else
        echo "❌ Ruff lint failed:"
        cat /tmp/cq_py_ruff.out
        ERRORS=1
    fi
}

run_mypy() {
    echo "🔍 Python: Type checking (mypy)..."
    if mypy . > /tmp/cq_py_mypy.out 2>&1; then
        echo "✅ mypy passed"
    else
        echo "❌ mypy failed:"
        cat /tmp/cq_py_mypy.out
        ERRORS=1
    fi
}

run_black() {
    if [ "$MODE" = "ci" ]; then
        echo "🔍 Python: Format check (black)..."
        if black --check . > /tmp/cq_py_black.out 2>&1; then
            echo "✅ Black format check passed"
        else
            echo "❌ Black format check failed:"
            cat /tmp/cq_py_black.out
            ERRORS=1
        fi
    else
        echo "🔧 Python: Format write (black)..."
        if black . > /tmp/cq_py_black.out 2>&1; then
            echo "✅ Black format write completed"
        else
            echo "❌ Black format write failed:"
            cat /tmp/cq_py_black.out
            ERRORS=1
        fi
    fi
}

run_ruff
run_mypy
run_black

exit $ERRORS