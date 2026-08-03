from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from scripts.rules_engine import (
    RULES,
    RULES_BY_ID,
    load_yaml_rules,
    review_files,
    rules_for_category,
    rules_payload,
    rules_to_dict,
    to_sarif,
)

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_STATE_DIR = SKILL_DIR / ".code-reviewer"


def _state_dir() -> Path:
    return Path(os.environ.get("CODE_REVIEWER_STATE_DIR", str(DEFAULT_STATE_DIR)))


def _load_state() -> dict:
    state_file = _state_dir() / "history.json"
    if not state_file.exists():
        return {"reviews": []}
    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"reviews": []}


def _save_state(state: dict) -> None:
    _state_dir().mkdir(exist_ok=True)
    (_state_dir() / "history.json").write_text(
        json.dumps(state, indent=2), encoding="utf-8"
    )


def _cmd_review(args: argparse.Namespace) -> int:
    files = args.files or []
    if args.incremental:
        base = args.base or "HEAD~1"
        import subprocess

        try:
            proc = subprocess.run(
                ["git", "-C", str(cwd), "diff", "--name-only", base],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode == 0:
                files = [line for line in proc.stdout.splitlines() if line.strip()]
            else:
                print(f"ERROR: git diff failed: {proc.stderr.strip()}")
                return 1
        except FileNotFoundError:
            print("ERROR: git executable not found")
            return 1

    cwd = Path(args.cwd or SKILL_DIR)
    result = review_files(files, cwd=cwd)
    findings = result["findings"]

    if args.ci:
        critical = result["summary"]["by_severity"].get("CRITICAL", 0)
        gate = args.max_critical if args.max_critical is not None else 0
        if critical > gate:
            print(
                json.dumps(result, indent=2)
                if args.format == "json"
                else json.dumps(result, indent=2)
            )
            print(
                f"GATE FAILED: {critical} critical finding(s) exceeds limit {gate}"
            )
            return 1

    if args.format == "sarif":
        print(json.dumps(to_sarif(findings), indent=2))
    else:
        print(json.dumps(result, indent=2))

    if findings:
        state = _load_state()
        state["reviews"].append(
            {
                "files": result["files_scanned"],
                "total_findings": result["summary"]["total_findings"],
                "score": result["summary"]["score"],
                "severities": result["summary"]["by_severity"],
            }
        )
        _save_state(state)

    return 0


def _cmd_rules(args: argparse.Namespace) -> int:
    rules = RULES
    if args.category:
        rules = rules_for_category(args.category)
        if not rules:
            print(f"ERROR: no rules found for category {args.category!r}")
            return 1
    if args.list:
        payload = rules_payload(rules)
        print(json.dumps(payload, indent=2))
        return 0
    if args.add:
        rule_file = Path(args.add)
        if not rule_file.exists():
            print(f"ERROR: rule file {rule_file} not found")
            return 1
        try:
            custom = load_yaml_rules(rule_file)
        except ImportError as exc:
            print(f"ERROR: {exc}")
            return 1
        existing = {
            rule["id"]
            for rule in _load_state().get("custom_rules", [])
        }
        added = []
        for rule in custom:
            if rule.id not in existing and rule.id not in RULES_BY_ID:
                added.append(rules_to_dict(rule))
        if not added:
            print("No new rules added (all ids already known)")
            return 0
        state = _load_state()
        state.setdefault("custom_rules", []).extend(added)
        _save_state(state)
        print(json.dumps({"added": added}, indent=2))
        return 0
    print(rules_payload(rules))
    return 0


def _cmd_history(args: argparse.Namespace) -> int:
    state = _load_state()
    reviews = state.get("reviews", [])
    if args.file:
        reviews = [r for r in reviews if args.file in r.get("files", [])]
    if args.limit and args.limit > 0:
        reviews = reviews[-args.limit :]
    print(json.dumps({"reviews": reviews}, indent=2))
    return 0


def _cmd_show_rule(args: argparse.Namespace) -> int:
    rule = RULES_BY_ID.get(args.rule)
    if rule is None:
        print(f"ERROR: unknown rule {args.rule!r}")
        return 1
    print(
        json.dumps(
            {
                "id": rule.id,
                "category": rule.category,
                "severity": rule.severity,
                "message": rule.message,
                "fix": rule.fix,
                "pattern": rule.pattern,
                "languages": rule.languages,
            },
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="code-reviewer")
    sub = parser.add_subparsers(dest="action", required=True)

    review = sub.add_parser("review")
    review.add_argument("--files", nargs="+", default=[])
    review.add_argument("--cwd")
    review.add_argument("--config")
    review.add_argument("--incremental", action="store_true")
    review.add_argument("--base", default="HEAD~1")
    review.add_argument("--ci", action="store_true")
    review.add_argument("--max-critical", type=int)
    review.add_argument("--format", choices=["json", "sarif"], default="json")
    review.set_defaults(func=_cmd_review)

    rules = sub.add_parser("rules")
    rules.add_argument("--list", action="store_true")
    rules.add_argument("--category")
    rules.add_argument("--add", metavar="FILE")
    rules.set_defaults(func=_cmd_rules)

    show = sub.add_parser("show")
    show.add_argument("rule", metavar="RULE_ID")
    show.set_defaults(func=_cmd_show_rule)

    history = sub.add_parser("history")
    history.add_argument("--file")
    history.add_argument("--limit", type=int)
    history.set_defaults(func=_cmd_history)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if hasattr(args, "func"):
        return args.func(args)
    build_parser().print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
