#!/bin/bash
# Output formatting utilities for code-quality reports.

REPORT_FORMAT="${REPORT_FORMAT:-text}"

print_header() {
    local title="$1"
    if [ "$REPORT_FORMAT" = "json" ]; then
        echo "{\"type\": \"header\", \"title\": \"$title\"}"
    else
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  $title"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    fi
}

print_result() {
    local name="$1"
    local status="$2"
    local details="${3:-}"
    if [ "$REPORT_FORMAT" = "json" ]; then
        printf '{"type": "result", "name": "%s", "status": "%s", "details": "%s"}\n' "$name" "$status" "$details"
    else
        local icon="✅"
        if [ "$status" != "pass" ]; then
            icon="❌"
        fi
        echo "$icon $name: $status"
        if [ -n "$details" ]; then
            echo "  $details"
        fi
    fi
}

print_summary() {
    local passed="$1"
    local failed="$2"
    local total=$((passed + failed))
    if [ "$REPORT_FORMAT" = "json" ]; then
        printf '{"type": "summary", "passed": %d, "failed": %d, "total": %d}\n' "$passed" "$failed" "$total"
    else
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📊 Summary: $passed passed, $failed failed ($total total)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    fi
}
