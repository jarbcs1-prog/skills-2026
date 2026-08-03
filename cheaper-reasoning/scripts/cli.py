"""CLI for cheaper-reasoning skill."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.quality import ContemplationQuality, QualityScore
from scripts.convergence import detect_convergence, ConvergenceSignal
from scripts.triggers import should_use_deep_reasoning, Task


def cmd_think(args: argparse.Namespace) -> int:
    contemplation = _read_input(args.input)
    quality = ContemplationQuality()
    score = quality.score(contemplation)
    convergence = detect_convergence([contemplation])

    result = {
        "topic": args.topic,
        "mode": args.mode,
        "budget_tokens": args.budget,
        "quality_score": score.to_dict(),
        "convergence": convergence.value,
        "contemplation_length": len(contemplation),
    }
    print(json.dumps(result, indent=2))
    return 0


def cmd_resume(args: argparse.Namespace) -> int:
    checkpoint = Path(args.checkpoint)
    if not checkpoint.exists():
        print(f"Checkpoint not found: {checkpoint}", file=sys.stderr)
        return 1
    data = json.loads(checkpoint.read_text())
    print(json.dumps({"resumed": True, "checkpoint": args.checkpoint, "state": data}, indent=2))
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    trace = Path(args.input)
    if not trace.exists():
        print(f"Trace file not found: {trace}", file=sys.stderr)
        return 1
    data = json.loads(trace.read_text())
    quality = ContemplationQuality()
    score = quality.score(data.get("contemplation", ""))
    result = {
        "trace": args.input,
        "quality": score.to_dict(),
        "convergence": detect_convergence(data.get("history", [])).value,
    }
    print(json.dumps(result, indent=2))
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    task = Task(
        complexity_score=args.complexity,
        uncertainty_level=args.uncertainty,
        requires_architecture_decision=args.architecture,
        has_conflicting_constraints=args.conflicting,
        user_explicitly_requested_reasoning=args.explicit,
    )
    decision = should_use_deep_reasoning(task)
    print(json.dumps({"use_deep_reasoning": decision.use, "reason": decision.reason, "confidence": decision.confidence}, indent=2))
    return 0


def _read_input(input_arg: str) -> str:
    path = Path(input_arg)
    if path.exists():
        return path.read_text()
    return input_arg


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="cheaper-reasoning",
        description="Contemplation-based reasoning with quality validation and convergence detection",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    think_p = subparsers.add_parser("think", help="Run a reasoning session")
    think_p.add_argument("--topic", required=True, help="Reasoning topic")
    think_p.add_argument("--input", default="", help="Input text or file path")
    think_p.add_argument("--mode", default="deep", choices=["quick", "standard", "deep"])
    think_p.add_argument("--budget", type=int, default=15000, help="Token budget")
    think_p.add_argument("--checkpoint", default="", help="Save checkpoint to file")

    resume_p = subparsers.add_parser("resume", help="Resume from checkpoint")
    resume_p.add_argument("--checkpoint", required=True, help="Checkpoint file path")

    analyze_p = subparsers.add_parser("analyze", help="Analyze a reasoning trace")
    analyze_p.add_argument("--input", required=True, help="Trace file path")

    check_p = subparsers.add_parser("check", help="Check if deep reasoning should be used")
    check_p.add_argument("--complexity", type=float, default=0.5, help="Complexity score (0-1)")
    check_p.add_argument("--uncertainty", type=float, default=0.5, help="Uncertainty level (0-1)")
    check_p.add_argument("--architecture", action="store_true", help="Requires architecture decision")
    check_p.add_argument("--conflicting", action="store_true", help="Has conflicting constraints")
    check_p.add_argument("--explicit", action="store_true", help="User explicitly requested reasoning")

    args = parser.parse_args()
    handlers = {
        "think": cmd_think,
        "resume": cmd_resume,
        "analyze": cmd_analyze,
        "check": cmd_check,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())