#!/bin/bash
set -euo pipefail

MODE="${1:-agent}"
CONFIG_FILE="${2:-.code-quality.yml}"

ERRORS=0

echo "🔍 Dependency vulnerability scanning..."

if [ -f "package.json" ]; then
    echo "📦 Checking npm dependencies..."
    if npm audit --audit-level=high > /tmp/cq_dep_npm.out 2>&1; then
        echo "✅ npm audit passed"
    else
        echo "⚠️  npm audit found issues:"
        cat /tmp/cq_dep_npm.out
    fi
fi

if [ -f "Cargo.toml" ]; then
    echo "📦 Checking Rust dependencies..."
    if cargo audit > /tmp/cq_dep_cargo.out 2>&1; then
        echo "✅ cargo audit passed"
    else
        echo "⚠️  cargo audit found issues:"
        cat /tmp/cq_dep_cargo.out
    fi
fi

if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    echo "📦 Checking Python dependencies..."
    if pip-audit > /tmp/cq_dep_pip.out 2>&1; then
        echo "✅ pip-audit passed"
    else
        echo "⚠️  pip-audit found issues:"
        cat /tmp/cq_dep_pip.out
    fi
fi

echo "✅ Dependency scanning completed"
exit $ERRORS