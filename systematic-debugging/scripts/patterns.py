"""Common bug pattern library for systematic-debugging skill."""
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class BugPattern:
    name: str
    symptoms: List[str]
    common_causes: List[str]
    investigation: List[str]
    fix_patterns: List[str]


BUG_PATTERNS: Dict[str, BugPattern] = {
    "null_pointer": BugPattern(
        name="Null Pointer / None Access",
        symptoms=[
            "AttributeError: 'NoneType' object has no attribute",
            "TypeError: None is not iterable",
            "KeyError: None key not found",
        ],
        common_causes=[
            "Missing null check before access",
            "Uninitialized variable",
            "Failed dictionary lookup returning None",
            "Function returning None unexpectedly",
        ],
        investigation=[
            "Trace variable assignment chain",
            "Check all code paths for None return",
            "Verify initialization in all branches",
            "Add assertions at point of use",
        ],
        fix_patterns=[
            "Early return with None check",
            "Default values with or operator",
            "Assertion before access",
            "Optional chaining pattern",
        ],
    ),
    "off_by_one": BugPattern(
        name="Off-by-One Error",
        symptoms=[
            "IndexError: list index out of range",
            "Missing last element in iteration",
            "Extra iteration in loop",
        ],
        common_causes=[
            "Using <= instead of < in loop condition",
            "range(len(x)) vs range(len(x)-1)",
            "0-indexed vs 1-indexed confusion",
            "Slice boundary confusion",
        ],
        investigation=[
            "Check loop boundary conditions",
            "Verify array/list length",
            "Trace index values at each iteration",
            "Test with empty and single-element inputs",
        ],
        fix_patterns=[
            "Use iterator instead of index",
            "Add boundary assertions",
            "Test edge cases explicitly",
        ],
    ),
    "race_condition": BugPattern(
        name="Race Condition",
        symptoms=[
            "Intermittent failures",
            "Corrupted or inconsistent data",
            "Deadlock or hang",
            "Non-deterministic results",
        ],
        common_causes=[
            "Shared mutable state without synchronization",
            "Non-atomic read-modify-write operations",
            "Missing locks or incorrect lock scope",
            "Thread-unsafe data structures",
        ],
        investigation=[
            "Add thread IDs to log messages",
            "Run stress test with high concurrency",
            "Check synchronization primitives",
            "Verify lock acquisition order",
        ],
        fix_patterns=[
            "Thread-local storage",
            "Proper lock usage",
            "Atomic operations",
            "Immutable data structures",
        ],
    ),
    "memory_leak": BugPattern(
        name="Memory Leak",
        symptoms=[
            "Growing memory usage over time",
            "OOM kills",
            "Progressive slowdown",
        ],
        common_causes=[
            "Unclosed resources (files, connections)",
            "Circular references",
            "Cache without eviction policy",
            "Accumulating event listeners",
        ],
        investigation=[
            "Run memory profiler",
            "Track object counts over time",
            "Analyze garbage collection behavior",
            "Check for unclosed context managers",
        ],
        fix_patterns=[
            "Use context managers (with statement)",
            "Weak references for caches",
            "Cache TTL / size limits",
            "Explicit cleanup in finally blocks",
        ],
    ),
    "import_cycle": BugPattern(
        name="Import Cycle",
        symptoms=[
            "ImportError at module load time",
            "Partial module initialization",
            "AttributeError on imported symbol",
        ],
        common_causes=[
            "Mutual imports between modules",
            "Import at module level instead of function level",
            "Circular dependency in package __init__.py",
        ],
        investigation=[
            "Check import graph for cycles",
            "Move imports inside functions",
            "Refactor shared code into third module",
        ],
        fix_patterns=[
            "Lazy imports inside functions",
            "Extract shared code to separate module",
            "Use TYPE_CHECKING guard for type imports",
        ],
    ),
}


def search_patterns(query: str, language: str = "python") -> List[BugPattern]:
    results = []
    query_lower = query.lower()
    for pattern in BUG_PATTERNS.values():
        if query_lower in pattern.name.lower():
            results.append(pattern)
        for symptom in pattern.symptoms:
            if query_lower in symptom.lower():
                if pattern not in results:
                    results.append(pattern)
                break
    return results


def get_pattern(name: str) -> Optional[BugPattern]:
    return BUG_PATTERNS.get(name)