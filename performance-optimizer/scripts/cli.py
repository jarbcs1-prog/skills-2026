from __future__ import annotations

import argparse
import glob as glob_module
import importlib.util
import json
import re
import sys
from html import escape
from pathlib import Path
from typing import Any

from .benchmark import BenchmarkHarness
from .profiler import Profiler
from .rules import PERFORMANCE_RULES, rules_for_language, scan_source

_UNIT_SCALES: dict[str, float] = {
    "ns": 1e-6,
    "us": 1e-3,
    "ms": 1.0,
    "s": 1000.0,
    "B": 1e-6,
    "KB": 1e-3,
    "MB": 1.0,
    "GB": 1000.0,
}

_VALUE_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([A-Za-z]*)\s*$")


def _emit(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _resolve_targets(target: str) -> list[Path]:
    candidates = glob_module.glob(target)
    if not candidates and Path(target).is_file():
        candidates = [target]
    return sorted(Path(candidate) for candidate in candidates if Path(candidate).is_file())


def _infer_language(command: str) -> str | None:
    lowered = command.lower()
    if "python" in lowered or " pip " in f" {command} ":
        return "python"
    if "node" in lowered:
        return "javascript"
    if "cargo" in lowered or "rustc" in lowered:
        return "rust"
    if "go run" in lowered or "go build" in lowered:
        return "go"
    if "java" in lowered:
        return "java"
    return None


def _load_bench_callable(suite: str) -> Any:
    path = Path(suite)
    spec = importlib.util.spec_from_file_location("perf_suite", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load suite: {suite}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    bench = getattr(module, "bench", None)
    if not callable(bench):
        raise ValueError("suite must define a callable named 'bench'")
    return bench


def _to_number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = _VALUE_RE.match(value)
        if match:
            return float(match.group(1)) * _UNIT_SCALES.get(match.group(2), 1.0)
    return None


def _parse_budget(budget: str) -> dict[str, float]:
    parsed: dict[str, float] = {}
    for part in budget.split(","):
        part = part.strip()
        if not part or "=" not in part:
            continue
        metric, _, raw = part.partition("=")
        number = _to_number(raw.strip())
        if number is not None:
            parsed[metric.strip()] = number
    return parsed


def _collect_metrics(data: Any, collected: list[tuple[str, float]]) -> None:
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                if key in ("results", "metrics"):
                    _collect_metrics(value, collected)
                continue
            number = _to_number(value)
            if number is not None:
                collected.append((str(key), number))
    elif isinstance(data, list):
        for entry in data:
            if isinstance(entry, dict) and "metric" in entry:
                number = _to_number(entry.get("value"))
                if number is not None:
                    collected.append((str(entry["metric"]), number))
            else:
                _collect_metrics(entry, collected)


def _render_html(data: Any) -> str:
    if isinstance(data, dict):
        findings = data.get("findings", data)
    else:
        findings = data
    if isinstance(findings, dict):
        findings = [findings]
    columns = ("rule_id", "severity", "message", "fix", "line")
    header = "<tr>" + "".join(f"<th>{column}</th>" for column in columns) + "</tr>"
    rows = []
    for finding in findings:
        cells = "".join(f"<td>{escape(str(finding.get(column, '')))}</td>" for column in columns)
        rows.append(f"<tr>{cells}</tr>")
    body = "".join(rows)
    return (
        "<html><body><h1>Performance Findings</h1>"
        f"<table><thead>{header}</thead><tbody>{body}</tbody></table>"
        "</body></html>"
    )


def _run_analyze(args: argparse.Namespace) -> int:
    files = _resolve_targets(args.target)
    if not files:
        _emit({"files": [], "findings": [], "error": "no files matched"})
        return 1
    findings: list[dict] = []
    for file_path in files:
        text = _read_text(file_path)
        for finding in scan_source(text, args.language):
            finding["file"] = str(file_path)
            findings.append(finding)
    output: dict[str, Any] = {"files": [str(file_path) for file_path in files], "findings": findings}
    if args.profile:
        hotspots = []
        for file_path in files:
            hotspots.append(
                {
                    "file": str(file_path),
                    "analysis": Profiler.analyze_hotspots(_read_text(file_path), args.language),
                }
            )
        output["profile"] = {"tools": Profiler.detect(args.language), "files": hotspots}
    _emit(output)
    return 0


def _run_profile(args: argparse.Namespace) -> int:
    language = _infer_language(args.command)
    tools = Profiler.detect(language) if language else []
    _emit(
        {
            "command": args.command,
            "duration": args.duration,
            "tools": tools,
            "note": "run under py-spy/cProfile for real traces",
        }
    )
    return 0


def _run_benchmark(args: argparse.Namespace) -> int:
    bench = _load_bench_callable(args.suite)
    harness = BenchmarkHarness()
    result = harness.run(bench, warmup=args.warmup, iterations=args.iterations)
    suite_name = Path(args.suite).stem
    output: dict[str, Any] = {"suite": args.suite, "name": suite_name, "results": result}
    if args.store_baseline:
        harness.store_baseline(suite_name, result)
        output["baseline"] = "stored"
    if args.compare_baseline:
        baseline = harness.get_baseline(suite_name)
        if baseline is None:
            output["compare"] = {"status": "no-baseline"}
        else:
            output["compare"] = harness.compare(result, baseline)
    _emit(output)
    return 0


def _run_rules_list(language: str | None) -> int:
    if language:
        _emit({"language": language, "rules": rules_for_language(language)})
    else:
        _emit({"languages": PERFORMANCE_RULES})
    return 0


def _run_rules_add(path: str) -> int:
    import yaml

    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    new_rules = list(data.get("rules", []))
    store_path = Path(".perf_rules.yaml")
    existing: list[dict] = []
    if store_path.exists():
        existing_data = yaml.safe_load(store_path.read_text(encoding="utf-8")) or {}
        existing = list(existing_data.get("rules", []))
    store_path.write_text(yaml.safe_dump({"rules": existing + new_rules}, sort_keys=False), encoding="utf-8")
    _emit({"added": len(new_rules)})
    return 0


def _run_rules(args: argparse.Namespace) -> int:
    if args.add:
        return _run_rules_add(args.add)
    return _run_rules_list(args.language)


def _run_report(args: argparse.Namespace) -> int:
    fmt = args.format.lower()
    if fmt not in ("json", "html"):
        _emit({"error": f"unsupported format: {args.format}"})
        return 1
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    output_path = Path(args.output)
    if fmt == "json":
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        output_path.write_text(_render_html(data), encoding="utf-8")
    _emit({"written": str(output_path)})
    return 0


def _run_gate(args: argparse.Namespace) -> int:
    budget = _parse_budget(args.budget)
    data = json.loads(Path(args.results).read_text(encoding="utf-8"))
    collected: list[tuple[str, float]] = []
    _collect_metrics(data, collected)
    violations: list[dict] = []
    for metric, value in collected:
        limit = budget.get(metric)
        if limit is not None and value > limit:
            violations.append({"metric": metric, "value": value, "limit": limit})
    passed = not violations
    output: dict[str, Any] = {"passed": passed, "budget": budget}
    if violations:
        output["violations"] = violations
    _emit(output)
    return 0 if passed else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="performance-optimizer",
        description="Performance analysis, benchmarking, and regression gating.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Scan target files for performance rules")
    analyze.add_argument("--target", required=True)
    analyze.add_argument("--language", required=True)
    analyze.add_argument("--profile", action="store_true")
    analyze.set_defaults(func=_run_analyze)

    profile = subparsers.add_parser("profile", help="Detect available profiling tools (stub)")
    profile.add_argument("--command", required=True)
    profile.add_argument("--duration", type=int, default=60)
    profile.set_defaults(func=_run_profile)

    benchmark = subparsers.add_parser("benchmark", help="Run a benchmark suite")
    benchmark.add_argument("--suite", required=True)
    benchmark.add_argument("--iterations", type=int, default=10)
    benchmark.add_argument("--warmup", type=int, default=3)
    benchmark.add_argument("--compare-baseline", action="store_true")
    benchmark.add_argument("--store-baseline", action="store_true")
    benchmark.set_defaults(func=_run_benchmark)

    rules = subparsers.add_parser("rules", help="List or add performance rules")
    rules.add_argument("--language")
    rules.add_argument("--list", action="store_true")
    rules.add_argument("--add")
    rules.set_defaults(func=_run_rules)

    report = subparsers.add_parser("report", help="Convert results into a report")
    report.add_argument("--input", required=True)
    report.add_argument("--format", required=True)
    report.add_argument("--output", required=True)
    report.set_defaults(func=_run_report)

    gate = subparsers.add_parser("gate", help="Enforce performance budgets")
    gate.add_argument("--budget", required=True)
    gate.add_argument("--results", required=True)
    gate.add_argument("--ci", action="store_true")
    gate.set_defaults(func=_run_gate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
