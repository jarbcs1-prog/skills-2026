#!/bin/bash
set -euo pipefail

MODE="${1:-agent}"
CONFIG_FILE="${2:-.code-quality.yml}"

ERRORS=0

run_cargo_check() {
    echo "🔍 Rust: cargo check..."
    if cargo check > /tmp/cq_rs_check.out 2>&1; then
        echo "✅ cargo check passed"
    else
        echo "❌ cargo check failed:"
        cat /tmp/cq_rs_check.out
        ERRORS=1
    fi
}

run_clippy() {
    echo "🔍 Rust: Clippy..."
    if cargo clippy -- -D warnings > /tmp/cq_rs_clippy.out 2>&1; then
        echo "✅ Clippy passed"
    else
        echo "❌ Clippy failed:"
        cat /tmp/cq_rs_clippy.out
        ERRORS=1
    fi
}

run_rustfmt() {
    if [ "$MODE" = "ci" ]; then
        echo "🔍 Rust: Format check (rustfmt)..."
        if rustfmt --check . > /tmp/cq_rs_fmt.out 2>&1; then
            echo "✅ rustfmt check passed"
        else
            echo "❌ rustfmt check failed:"
            cat /tmp/cq_rs_fmt.out
            ERRORS=1
        fi
    else
        echo "🔧 Rust: Format write (rustfmt)..."
        if rustfmt . > /tmp/cq_rs_fmt.out 2>&1; then
            echo "✅ rustfmt format write completed"
        else
            echo "❌ rustfmt format write failed:"
            cat /tmp/cq_rs_fmt.out
            ERRORS=1
        fi
    fi
}

run_cargo_check
run_clippy
run_rustfmt

exit $ERRORS