"""Benchmarks token reduction ratios across compaction strategies.

Creates synthetic context of varying sizes, applies compaction with
different strategies, and outputs a comparison table measuring:
  - tokens before / after
  - reduction ratio
  - wall-clock time elapsed

Usage:
    python benchmark_context_reduction.py
    python benchmark_context_reduction.py --sizes 10000 50000 --strategy token_budget
    python benchmark_context_reduction.py --iterations 5 --all-strategies
"""

import argparse
import json
import sys
import time
from typing import List, Dict, Any

from compaction import Compactor


# ---------------------------------------------------------------------------
# Synthetic context generation
# ---------------------------------------------------------------------------

def _estimate_tokens(context: List[Dict[str, Any]]) -> int:
    """Rough token estimate: ~4 chars per token."""
    return len(json.dumps(context, sort_keys=True)) // 4


def generate_context(target_tokens: int) -> List[Dict[str, Any]]:
    """Build a synthetic context history that is approximately *target_tokens* long."""
    context: List[Dict[str, Any]] = []
    # Each synthetic turn is ~120 tokens (approx 480 chars)
    turn_tokens = 120
    n_turns = max(target_tokens // turn_tokens, 2)

    for i in range(n_turns):
        context.append({
            "role": "user",
            "type": "message",
            "content": f"Step {i}: Please perform action-{i} on the codebase. "
                       f"This is a synthetic instruction to inflate context size.",
        })
        context.append({
            "role": "assistant",
            "type": "tool_call",
            "tool": "bash" if i % 3 == 0 else "edit" if i % 3 == 1 else "read",
            "call_id": f"call_{i:06d}",
            "input": {"command": f"echo step-{i}" if i % 3 == 0 else {"file": f"src/step_{i}.py"}},
            "output": f"Completed step {i}. Output: {'x' * 200}",
        })

    return context


# ---------------------------------------------------------------------------
# Strategy configs (maps strategy name → compact_ratio)
# ---------------------------------------------------------------------------

STRATEGIES = {
    "token_budget": 0.4,
    "age_based": 0.5,
    "hybrid": 0.6,
}


def run_benchmark(
    target_tokens: int,
    strategy: str,
    keep_recent_full: int = 5,
) -> Dict[str, Any]:
    """Run a single benchmark trial and return metrics."""
    compact_ratio = STRATEGIES[strategy]
    compactor = Compactor(
        keep_recent_full=keep_recent_full,
        compact_ratio=compact_ratio,
        preserve_structure=True,
    )

    context = generate_context(target_tokens)
    tokens_before = _estimate_tokens(context)

    t0 = time.perf_counter()
    compacted, offloaded = compactor.compact(context)
    elapsed = time.perf_counter() - t0

    tokens_after = _estimate_tokens(compacted)
    tokens_offloaded = _estimate_tokens(offloaded)
    reduction = 1.0 - (tokens_after / tokens_before) if tokens_before else 0.0

    return {
        "strategy": strategy,
        "target_tokens": target_tokens,
        "actual_tokens_before": tokens_before,
        "tokens_after": tokens_after,
        "tokens_offloaded": tokens_offloaded,
        "reduction_ratio": round(reduction, 4),
        "items_before": len(context),
        "items_after": len(compacted),
        "items_offloaded": len(offloaded),
        "elapsed_ms": round(elapsed * 1000, 2),
    }


# ---------------------------------------------------------------------------
# Table output
# ---------------------------------------------------------------------------

def print_table(results: List[Dict[str, Any]]) -> None:
    """Pretty-print benchmark results as a fixed-width table."""
    headers = [
        "Strategy",
        "Target",
        "Before",
        "After",
        "Offloaded",
        "Reduction",
        "Items In",
        "Items Out",
        "Time (ms)",
    ]
    widths = [max(len(h), 12) for h in headers]
    row_fmt = "".join(f"{{:<{w}}}" for w in widths)

    print(row_fmt.format(*headers))
    print("-" * sum(widths))

    for r in results:
        print(row_fmt.format(
            r["strategy"],
            f"{r['target_tokens']:,}",
            f"{r['actual_tokens_before']:,}",
            f"{r['tokens_after']:,}",
            f"{r['tokens_offloaded']:,}",
            f"{r['reduction_ratio']:.1%}",
            str(r["items_before"]),
            str(r["items_after"]),
            f"{r['elapsed_ms']:.1f}",
        ))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark context reduction across compaction strategies.",
    )
    parser.add_argument(
        "--sizes",
        type=int,
        nargs="+",
        default=[10_000, 50_000, 100_000],
        help="Target token sizes to test (default: 10000 50000 100000).",
    )
    parser.add_argument(
        "--strategy",
        choices=list(STRATEGIES.keys()),
        default=None,
        help="Run a single strategy (default: run all).",
    )
    parser.add_argument(
        "--all-strategies",
        action="store_true",
        help="Run all strategies (default behavior).",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Number of iterations per (size, strategy) pair (default: 1).",
    )
    parser.add_argument(
        "--keep-recent",
        type=int,
        default=5,
        help="Number of recent items to keep verbatim (default: 5).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON instead of a table.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.strategy:
        strategies = [args.strategy]
    else:
        strategies = list(STRATEGIES.keys())

    results: List[Dict[str, Any]] = []

    for size in args.sizes:
        for strat in strategies:
            for iteration in range(args.iterations):
                result = run_benchmark(
                    target_tokens=size,
                    strategy=strat,
                    keep_recent_full=args.keep_recent,
                )
                result["iteration"] = iteration + 1
                results.append(result)

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print_table(results)
        print(f"\nTotal benchmarks: {len(results)}")


if __name__ == "__main__":
    main()
