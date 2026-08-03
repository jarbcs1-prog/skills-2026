#!/bin/bash
set -euo pipefail

MODE="${1:-agent}"
CONFIG_FILE="${2:-.code-quality.yml}"

ERRORS=0

MARKDOWN_FILES=$(find . -type f -name "*.md" \
    -not -path "./node_modules/*" \
    -not -path "./.next/*" \
    -not -path "./.git/*" \
    -not -path "./dist/*" \
    -not -path "./build/*" \
    -not -path "./.ada/*" \
    -not -path "./.cursor/*" \
    2>/dev/null | sort || echo "")

if [ -z "$MARKDOWN_FILES" ]; then
    echo "✅ No markdown files found"
    exit 0
fi

MARKDOWN_COUNT=$(echo "$MARKDOWN_FILES" | wc -l | xargs)
echo "📝 Checking $MARKDOWN_COUNT markdown file(s)..."

ISSUES=0

while IFS= read -r file; do
    if [ -z "$file" ]; then
        continue
    fi

    if grep -l '[[:space:]]$' "$file" >/dev/null 2>&1; then
        echo "  ⚠️  $file: Contains trailing whitespace"
        ISSUES=$((ISSUES + 1))
    fi

    if [ -s "$file" ] && [ "$(tail -c 1 "$file" | wc -c)" -gt 0 ] && [ "$(tail -c 1 "$file")" != "$(printf '\n')" ]; then
        echo "  ⚠️  $file: Missing newline at end of file"
        ISSUES=$((ISSUES + 1))
    fi
done <<< "$MARKDOWN_FILES"

if [ "$ISSUES" -eq 0 ]; then
    echo "✅ No markdown issues found"
else
    echo "❌ Found $ISSUES markdown issue(s)"
    ERRORS=1
fi

exit $ERRORS