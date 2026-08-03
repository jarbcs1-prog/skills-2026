#!/bin/bash
set -euo pipefail

MODE="${1:-agent}"
CONFIG_FILE="${2:-.code-quality.yml}"

ERRORS=0

run_go_vet() {
    echo "🔍 Go: vet..."
    if go vet ./... > /tmp/cq_go_vet.out 2>&1; then
        echo "✅ go vet passed"
    else
        echo "❌ go vet failed:"
        cat /tmp/cq_go_vet.out
        ERRORS=1
    fi
}

run_golangci_lint() {
    echo "🔍 Go: golangci-lint..."
    if golangci-lint run > /tmp/cq_go_lint.out 2>&1; then
        echo "✅ golangci-lint passed"
    else
        echo "❌ golangci-lint failed:"
        cat /tmp/cq_go_lint.out
        ERRORS=1
    fi
}

run_gofmt() {
    if [ "$MODE" = "ci" ]; then
        echo "🔍 Go: Format check (gofmt)..."
        UNFORMATTED=$(gofmt -l . 2>/dev/null || true)
        if [ -z "$UNFORMATTED" ]; then
            echo "✅ gofmt check passed"
        else
            echo "❌ gofmt check failed: unformatted files:"
            echo "$UNFORMATTED"
            ERRORS=1
        fi
    else
        echo "🔧 Go: Format write (gofmt)..."
        gofmt -w . > /tmp/cq_go_fmt.out 2>&1
        echo "✅ gofmt format write completed"
    fi
}

run_go_vet
run_golangci_lint
run_gofmt

exit $ERRORS