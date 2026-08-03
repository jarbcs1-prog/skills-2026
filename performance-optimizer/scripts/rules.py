from __future__ import annotations

import re

PERFORMANCE_RULES: dict[str, list[dict]] = {
    "python": [
        {
            "id": "py-string-concat-loop",
            "severity": "HIGH",
            "pattern": r"(\w+\s*=\s*\w+\s*\+=\s*['\"])",
            "message": "String concatenation in a loop; use ''.join(...)",
            "fix": "Collect parts in a list and ''.join(parts)",
        },
        {
            "id": "py-list-comp-vs-loop",
            "severity": "MEDIUM",
            "pattern": r"for\s+\w+\s+in\s+\w+:\s*\n\s*(append|extend)\(",
            "message": "Manual loop with append; prefer a list comprehension",
            "fix": "Replace the loop with a list comprehension",
        },
        {
            "id": "py-dict-get-vs-in",
            "severity": "LOW",
            "pattern": r"if\s+\w+\s+in\s+\w+dict",
            "message": "Prefer dict.get(...)",
            "fix": "Use dict.get(key, default) instead of membership check",
        },
        {
            "id": "py-generator-vs-list",
            "severity": "MEDIUM",
            "pattern": r"sum\(\s*\[",
            "message": "Prefer a generator expression to a list in sum()",
            "fix": "Use sum(x for x in items) without the brackets",
        },
    ],
    "database": [
        {
            "id": "db-n-plus-one",
            "severity": "CRITICAL",
            "pattern": r"for\s+\w+\s+in\s+\w+:\s*\n.*(query|select|execute)",
            "message": "Possible N+1 query pattern",
            "fix": "Use JOIN or batch loading (select_related, prefetch_related)",
        },
        {
            "id": "db-missing-index",
            "severity": "HIGH",
            "pattern": r"(WHERE|ORDER BY)\s+\w+\s*(=|IN)",
            "message": "Filtered/ordered column may need an index",
            "fix": "Add an index on the filtered or ordered column",
        },
        {
            "id": "db-select-star",
            "severity": "MEDIUM",
            "pattern": r"SELECT\s+\*",
            "message": "Avoid SELECT *; list columns explicitly",
            "fix": "Select only the columns you need",
        },
    ],
    "javascript": [
        {
            "id": "js-sync-in-loop",
            "severity": "HIGH",
            "pattern": r"for\s*\(.*\).*\n.*(await|sync)",
            "message": "Synchronous work in a loop blocks the event loop",
            "fix": "Batch work or schedule it asynchronously",
        },
        {
            "id": "js-large-bundle",
            "severity": "HIGH",
            "pattern": r"from\s+['\"](lodash|moment|react-dom/server)",
            "message": "Heavy import can inflate bundle",
            "fix": "Import only the parts used or switch to a lighter library",
        },
    ],
    "rust": [
        {
            "id": "rs-clone-in-loop",
            "severity": "HIGH",
            "pattern": r"for\s+\w+\s+in\s+\w+\.iter\(\)\s*\{\s*\n\s*.*\.clone\(\)",
            "message": "Cloning inside a loop; prefer borrowing",
            "fix": "Use references or iterators instead of clone()",
        },
        {
            "id": "rs-push-str-in-loop",
            "severity": "MEDIUM",
            "pattern": r"for\s+\w+\s+in\s+\w+[^{]*\{\s*\n\s*.*\.push_str\(",
            "message": "Repeated push_str in a loop",
            "fix": "Build a Vec<String> and join it once",
        },
        {
            "id": "rs-unbounded-growth",
            "severity": "LOW",
            "pattern": r"Vec::with_capacity\s*\(\s*0\s*\)",
            "message": "Vec with capacity 0 may cause repeated reallocation",
            "fix": "Reserve capacity with Vec::with_capacity(n)",
        },
    ],
    "go": [
        {
            "id": "go-append-in-loop",
            "severity": "HIGH",
            "pattern": r"for\s*[^\n]*\{\s*\n\s*\w+\s*=\s*append\(",
            "message": "Repeated append may reallocate; pre-allocate",
            "fix": "Pre-allocate with make([]T, 0, n)",
        },
        {
            "id": "go-string-concat-loop",
            "severity": "MEDIUM",
            "pattern": r"for\s*[^\n]*\{\s*\n\s*\w+\s*\+=\s*['\"]",
            "message": "String concatenation in a loop is O(n^2)",
            "fix": "Use strings.Builder",
        },
        {
            "id": "go-lock-in-loop",
            "severity": "LOW",
            "pattern": r"for\s*[^\n]*\{\s*\n.*\.(Lock|RLock)\(",
            "message": "Locking inside a loop can cause contention",
            "fix": "Hoist lock acquisition or batch operations",
        },
    ],
    "java": [
        {
            "id": "java-string-concat-loop",
            "severity": "HIGH",
            "pattern": r"for\s*\([^)]*\)\s*\{\s*\n\s*\w+\s*\+=\s*['\"]",
            "message": "String += in a loop creates many objects",
            "fix": "Use StringBuilder.append",
        },
        {
            "id": "java-list-add-in-loop",
            "severity": "MEDIUM",
            "pattern": r"for\s*\([^)]*\)\s*\{\s*\n\s*\w+\.add\(",
            "message": "Repeated add() in a loop; pre-size the collection",
            "fix": "new ArrayList<>(expectedSize)",
        },
        {
            "id": "java-boxed-in-loop",
            "severity": "LOW",
            "pattern": r"for\s*\([^)]*\)\s*\{\s*\n.*(Integer|Long|Double)\s*\(",
            "message": "Boxing in a loop; prefer primitives",
            "fix": "Use primitive types (int, long, double)",
        },
    ],
}


def rules_for_language(language: str) -> list[dict]:
    return PERFORMANCE_RULES.get(language, [])


def scan_source(text: str, language: str) -> list[dict]:
    findings: list[dict] = []
    for rule in rules_for_language(language):
        flags = re.MULTILINE if "\n" in rule["pattern"] else 0
        for match in re.finditer(rule["pattern"], text, flags):
            line = text.count("\n", 0, match.start()) + 1
            findings.append(
                {
                    "rule_id": rule["id"],
                    "severity": rule["severity"],
                    "message": rule["message"],
                    "fix": rule["fix"],
                    "line": line,
                }
            )
    return findings
