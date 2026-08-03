"""Command-line interface for the strategy-advisor skill."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.decision_matrix import DecisionMatrix
from scripts.frameworks import analyze
from scripts.scenario import ScenarioPlanner
from scripts.templates import render_template


def _parse_inputs(items: list[str]) -> dict[str, str]:
    inputs = {}
    for item in items:
        name, sep, value = item.partition("=")
        if sep:
            inputs[name] = value
    return inputs


def _parse_variables(text: str) -> dict[str, float]:
    variables = {}
    for part in text.split(","):
        if not part.strip():
            continue
        key, sep, value = part.partition("=")
        if sep:
            variables[key.strip()] = float(value)
    return variables


def cmd_analyze(args: argparse.Namespace) -> int:
    try:
        result = analyze(args.framework, args.topic, _parse_inputs(args.input))
    except KeyError:
        print(f"Unknown framework: {args.framework}", file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


def cmd_decide(args: argparse.Namespace) -> int:
    options = [o.strip() for o in args.options.split(",")]
    criteria = [c.strip() for c in args.criteria.split(",")]
    weights = [float(w) for w in args.weights.split(",") if w.strip()] if args.weights else None
    try:
        matrix = DecisionMatrix(options, criteria, weights)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(matrix.evaluate_with_sensitivity()))
    return 0


def cmd_scenario(args: argparse.Namespace) -> int:
    base = _parse_variables(args.variables)
    planner = ScenarioPlanner(base)
    if args.monte_carlo:
        result = {"strategy": args.strategy, "monte_carlo": planner.monte_carlo(iterations=args.iterations)}
    else:
        result = {"strategy": args.strategy, **planner.generate_scenarios()}
    print(json.dumps(result))
    return 0


def cmd_template(args: argparse.Namespace) -> int:
    try:
        content = render_template(args.type, args.topic)
    except KeyError:
        print(f"Unknown template type: {args.type}", file=sys.stderr)
        return 1
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
        print(json.dumps({"type": args.type, "output": args.output}))
    else:
        print(json.dumps({"type": args.type, "content": content}))
    return 0


def cmd_monitor(args: argparse.Namespace) -> int:
    kpis = [k.strip() for k in args.kpis.split(",")]
    result = {
        "strategy": args.strategy,
        "kpis": kpis,
        "monitoring": {
            "cadence": "weekly",
            "thresholds": "flag when KPI moves >10% from plan",
        },
    }
    print(json.dumps(result))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="strategy-advisor",
        description="Strategic analysis, decision matrices, scenario planning, and templates",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_p = subparsers.add_parser("analyze", help="Run a strategic framework analysis")
    analyze_p.add_argument("--framework", required=True, help="Framework id (e.g. swot)")
    analyze_p.add_argument("--topic", required=True, help="Topic to analyze")
    analyze_p.add_argument("--input", action="append", default=[], help="Dimension=text (repeatable)")

    decide_p = subparsers.add_parser("decide", help="Evaluate options with a weighted decision matrix")
    decide_p.add_argument("--options", required=True, help="Comma-separated options")
    decide_p.add_argument("--criteria", required=True, help="Comma-separated criteria")
    decide_p.add_argument("--weights", default="", help="Comma-separated weights")

    scenario_p = subparsers.add_parser("scenario", help="Generate strategy scenarios")
    scenario_p.add_argument("--strategy", required=True, help="Strategy being assessed")
    scenario_p.add_argument("--variables", default="", help="Comma-separated key=value variables")
    scenario_p.add_argument("--monte-carlo", action="store_true", help="Run Monte Carlo analysis")
    scenario_p.add_argument("--iterations", type=int, default=1000, help="Monte Carlo iterations")

    template_p = subparsers.add_parser("template", help="Render a strategy template")
    template_p.add_argument("--type", required=True, help="Template type")
    template_p.add_argument("--topic", default="untitled strategy", help="Topic for the template")
    template_p.add_argument("--output", default="", help="Write rendered content to a file")

    monitor_p = subparsers.add_parser("monitor", help="Define strategy monitoring KPIs")
    monitor_p.add_argument("--strategy", required=True, help="Strategy name")
    monitor_p.add_argument("--kpis", required=True, help="Comma-separated KPI names")

    args = parser.parse_args()

    handlers = {
        "analyze": cmd_analyze,
        "decide": cmd_decide,
        "scenario": cmd_scenario,
        "template": cmd_template,
        "monitor": cmd_monitor,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
