"""Command line interface for the skill-reviewer skill."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.skill_reviewer import check_consistency, review_skill

REPORT_FILENAME = "skill-reviewer-consistency-report.md"


def _emit(data: dict, code: int = 0) -> int:
    print(json.dumps(data, indent=2, default=str))
    return code


def _find_skills(skills_dir: Path) -> list[Path]:
    if not skills_dir.is_dir():
        return []
    return sorted(path for path in skills_dir.iterdir() if (path / "SKILL.md").is_file())


def _cmd_review(args: argparse.Namespace) -> int:
    if args.skill:
        result = review_skill(args.skill)
        result.pop("content", None)
        return _emit(result, 0 if result["passed"] else 1)

    entries = []
    for skill in _find_skills(Path(args.skills_dir)):
        result = review_skill(skill)
        entries.append(
            {
                "path": str(skill),
                "name": result["name"],
                "score": result["score"],
                "passed": result["passed"],
            }
        )
    data = {"skills": entries, "passed_count": sum(1 for e in entries if e["passed"]), "total": len(entries)}
    if args.output:
        output = Path(args.output)
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["path", "name", "score", "passed"])
            writer.writeheader()
            writer.writerows(entries)
        data["report"] = str(output)
    code = 0 if all(entry["score"] >= args.threshold for entry in entries) else 1
    return _emit(data, code)


def _period_delta(period: str) -> timedelta:
    match = re.match(r"^(\d+)([dwmy])$", period)
    if not match:
        return timedelta(days=30)
    number = int(match.group(1))
    unit = match.group(2)
    if unit == "d":
        return timedelta(days=number)
    if unit == "w":
        return timedelta(weeks=number)
    if unit == "m":
        return timedelta(days=30 * number)
    return timedelta(days=365 * number)


def _load_history(history_path: Path) -> list[dict]:
    if not history_path.is_file():
        return []
    try:
        data = json.loads(history_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def _cmd_health(args: argparse.Namespace) -> int:
    result = review_skill(args.skill)
    history_path = Path(args.skill) / ".skill-reviewer" / "health.json"
    history = _load_history(history_path)
    if args.track:
        entry = {"timestamp": datetime.now(timezone.utc).isoformat(), "score": result["score"]}
        history.append(entry)
        history_path.parent.mkdir(parents=True, exist_ok=True)
        history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")

    cutoff = datetime.now(timezone.utc) - _period_delta(args.period)
    filtered = []
    for item in history:
        try:
            timestamp = item.get("timestamp", "").replace("Z", "+00:00")
            parsed = datetime.fromisoformat(timestamp)
        except (AttributeError, TypeError, ValueError):
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        if parsed >= cutoff:
            filtered.append(item)

    trend = "flat"
    if len(filtered) >= 2:
        delta = filtered[-1]["score"] - filtered[-2]["score"]
        if delta > 0:
            trend = f"+{delta}"
        elif delta < 0:
            trend = f"-{abs(delta)}"
    return _emit({"score": result["score"], "passed": result["passed"], "history": filtered, "trend": trend})


def _cmd_consistency(args: argparse.Namespace) -> int:
    entries = []
    for skill in _find_skills(Path(args.skills_dir)):
        result = check_consistency(skill)
        entries.append(
            {
                "path": str(skill),
                "consistent": result["consistent"],
                "missing_references": result["missing_references"],
            }
        )
    data = {"skills": entries}
    if args.report:
        report_path = Path.cwd() / REPORT_FILENAME
        lines = ["# Skill Reviewer Consistency Report", ""]
        lines.append("| Skill | Consistent | Missing References |")
        lines.append("|-------|------------|--------------------|")
        for entry in entries:
            missing = ", ".join(entry["missing_references"]) or "none"
            lines.append(f"| {entry['path']} | {entry['consistent']} | {missing} |")
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        data["report"] = str(report_path)
    return _emit(data)


def _cmd_evaluate(args: argparse.Namespace) -> int:
    result = review_skill(args.skill)
    return _emit(
        {"name": result["name"], "score": result["score"], "passed": result["passed"], "fixes": result["fixes"]}
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skill-reviewer", description="Deterministic reviewer for agent skill packages.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_review = subparsers.add_parser("review", help="Review a single skill or a batch of skills.")
    target = parser_review.add_mutually_exclusive_group(required=True)
    target.add_argument("--skill", help="Path to a skill directory containing SKILL.md.")
    target.add_argument("--skills-dir", help="Path to a directory of skills for batch review.")
    parser_review.add_argument("--mode", choices=["self", "pr"], default="self", help="Review mode.")
    parser_review.add_argument("--batch", action="store_true", help="Review every skill under --skills-dir.")
    parser_review.add_argument("--output", help="Write batch results to a CSV file.")
    parser_review.add_argument("--threshold", type=int, default=70, help="Pass threshold for batch scores.")

    parser_health = subparsers.add_parser("health", help="Report skill health and optional score history.")
    parser_health.add_argument("--skill", required=True, help="Path to a skill directory.")
    parser_health.add_argument("--track", action="store_true", help="Append this review to the health history.")
    parser_health.add_argument("--period", default="30d", help="History window, e.g. 30d or 8w.")

    parser_consistency = subparsers.add_parser("consistency", help="Check referenced files exist across skills.")
    parser_consistency.add_argument("--skills-dir", required=True, help="Path to a directory of skills.")
    parser_consistency.add_argument(
        "--report", action="store_true", help="Write a markdown report to the current directory."
    )

    parser_evaluate = subparsers.add_parser("evaluate", help="Alias printing name, score, passed and fixes.")
    parser_evaluate.add_argument("--skill", required=True, help="Path to a skill directory.")

    args = parser.parse_args(argv)
    if args.command == "review":
        if args.skill and args.batch:
            parser.error("--batch cannot be combined with --skill")
        if args.skills_dir and not args.batch:
            parser.error("--batch is required when using --skills-dir")
        return _cmd_review(args)
    if args.command == "health":
        return _cmd_health(args)
    if args.command == "consistency":
        return _cmd_consistency(args)
    if args.command == "evaluate":
        return _cmd_evaluate(args)
    parser.error(f"Unknown command: {args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
