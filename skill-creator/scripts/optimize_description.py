"""Description optimization loop.

Wraps :mod:`scripts.run_loop` so a skill's description can be iteratively
improved against a trigger eval set. The heavy lifting (opencode CLI calls)
only runs when ``run_loop`` is available and a model is configured; the CLI
itself is thin and testable without an LLM.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class OptimizationResult:
    """Outcome of a description optimization run."""

    optimized: bool
    message: str
    data: dict | None = None

    def summary(self) -> str:
        return self.message


def _load_eval_set(eval_set_path: str | Path) -> dict:
    path = Path(eval_set_path)
    if not path.exists():
        raise FileNotFoundError(f"eval set {path} does not exist")
    return json.loads(path.read_text(encoding="utf-8"))


class DescriptionOptimizer:
    """Iteratively improve a skill description against trigger evals."""

    def __init__(self, model: str) -> None:
        self.model = model

    def optimize(
        self,
        skill_path: str | Path,
        eval_set: str | Path,
        max_iterations: int = 5,
        holdout: float = 0.4,
        runs_per_query: int = 3,
        trigger_threshold: float = 0.5,
        num_workers: int = 10,
        timeout: int = 30,
        results_dir: str | Path | None = None,
        verbose: bool = False,
    ) -> OptimizationResult:
        """Run the optimization loop, returning a result (or raising)."""
        skill_dir = Path(skill_path)
        if not (skill_dir / "SKILL.md").exists():
            raise FileNotFoundError(f"no SKILL.md in {skill_dir}")

        eval_data = _load_eval_set(eval_set)

        try:
            from scripts.run_loop import run_loop
        except ImportError as exc:
            return OptimizationResult(
                optimized=False,
                message=f"optimization requires scripts.run_loop: {exc}",
            )

        data = run_loop(
            eval_set=eval_data,
            skill_path=str(skill_dir),
            description_override=None,
            num_workers=num_workers,
            timeout=timeout,
            max_iterations=max_iterations,
            runs_per_query=runs_per_query,
            trigger_threshold=trigger_threshold,
            holdout=holdout,
            model=self.model,
            verbose=verbose,
            live_report_path=None,
            log_dir=str(results_dir) if results_dir else None,
        )
        best_score = float(data.get("best_score", 0))
        message = (
            f"Optimization finished: {data.get('exit_reason', 'done')} "
            f"(best score {best_score:.2f})"
        )
        return OptimizationResult(optimized=True, message=message, data=data)


def main() -> None:
    parser = argparse.ArgumentParser(prog="skill-creator-optimize")
    parser.add_argument("--skill-path", required=True)
    parser.add_argument("--eval-set", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--max-iterations", type=int, default=5)
    parser.add_argument("--holdout", type=float, default=0.4)
    parser.add_argument("--runs-per-query", type=int, default=3)
    parser.add_argument("--trigger-threshold", type=float, default=0.5)
    parser.add_argument("--num-workers", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--results-dir")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    try:
        optimizer = DescriptionOptimizer(args.model)
        result = optimizer.optimize(
            args.skill_path,
            args.eval_set,
            max_iterations=args.max_iterations,
            holdout=args.holdout,
            runs_per_query=args.runs_per_query,
            trigger_threshold=args.trigger_threshold,
            num_workers=args.num_workers,
            timeout=args.timeout,
            results_dir=args.results_dir,
            verbose=args.verbose,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    print(result.summary())
    if result.data:
        print(json.dumps(result.data, indent=2))
    sys.exit(0 if result.optimized else 1)


if __name__ == "__main__":
    main()
