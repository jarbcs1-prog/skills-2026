#!/usr/bin/env python3
"""CLI for verification-before-completion skill.

Evidence before claims, always. This CLI turns the Iron Law into a command:
run the verification command, read the output, only then claim the result.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import templates as template_lib
from .verifier import AgentVerifier, VerificationEngine, VerificationStep


def _default_history() -> Path:
    return Path.home() / ".verify" / "history.jsonl"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="verify",
        description="Evidence-before-claims verification runner",
    )
    subparsers = parser.add_subparsers(dest="action", help="Available commands")
    subparsers.required = True

    tests = subparsers.add_parser("tests", help="Run the test command and check the result")
    tests.add_argument("--command", required=True, help="Test command to execute")
    tests.add_argument("--expect", default="pass", help="pass, fail, or an output regex")
    tests.add_argument("--project", default=".", help="Project directory (cwd for the command)")
    tests.add_argument("--history", default="", help="History file (default: ~/.verify/history.jsonl)")

    build = subparsers.add_parser("build", help="Run the build command and require exit 0")
    build.add_argument("--command", required=True, help="Build command to execute")
    build.add_argument("--project", default=".", help="Project directory (cwd for the command)")
    build.add_argument("--history", default="", help="History file (default: ~/.verify/history.jsonl)")

    linter = subparsers.add_parser("linter", help="Run the linter and require exit 0")
    linter.add_argument("--command", required=True, help="Linter command to execute")
    linter.add_argument("--project", default=".", help="Project directory (cwd for the command)")
    linter.add_argument("--history", default="", help="History file (default: ~/.verify/history.jsonl)")

    requirements = subparsers.add_parser("requirements", help="Verify a requirements checklist")
    requirements.add_argument("--checklist", required=True, help="Markdown checklist file")
    requirements.add_argument("--all", action="store_true", help="Require every item checked")

    agent = subparsers.add_parser("agent", help="Verify an agent's completion claim against VCS diff")
    agent.add_argument("--task", required=True, help="Task description claimed complete")
    agent.add_argument("--claimed-files", required=True, help="Comma-separated files the agent claims to have changed")
    agent.add_argument("--project", default=".", help="Project directory")

    all_cmd = subparsers.add_parser("all", help="Run all template verification steps for the project")
    all_cmd.add_argument("--project", default=".", help="Project directory")
    all_cmd.add_argument("--type", default="", help="Project type (auto-detected if empty)")
    all_cmd.add_argument("--phase", default="pre-commit", help="pre-commit, pre-push, or pre-deploy")
    all_cmd.add_argument("--gate", action="store_true", help="Exit non-zero if any step fails")
    all_cmd.add_argument("--history", default="", help="History file (default: ~/.verify/history.jsonl)")
    all_cmd.add_argument("--override", default="", help="Emergency override reason (bypasses gate with audit trail)")

    history = subparsers.add_parser("history", help="Show verification history and compliance stats")
    history.add_argument("--period", default="30d", help="Lookback period, e.g. 30d or 0 for all")
    history.add_argument("--stats", action="store_true", help="Print compliance report")
    history.add_argument("--history", default="", help="History file (default: ~/.verify/history.jsonl)")

    coach = subparsers.add_parser("coach", help="Coaching guidance for verification discipline")
    coach.add_argument("--mode", default="strict", choices=["strict", "guided", "permissive"])

    return parser


def _engine(args: argparse.Namespace) -> VerificationEngine:
    history = Path(args.history) if args.history else _default_history()
    return VerificationEngine(history_path=history)


def _run_command_step(args: argparse.Namespace, expected: str) -> int:
    engine = _engine(args)
    step = VerificationStep(name=args.command.split()[0] if args.command.split() else "verify", command=args.command, expected=expected)
    result = engine.run_step(step)
    print(f"[{('PASS' if result.passed else 'FAIL')}] {result.name}")
    print(f"  command: {result.command}")
    if result.output:
        print(f"  output:  {result.output[:300]}")
    print(f"  reason:  {result.reason}")
    return 0 if result.passed else 1


def cmd_requirements(args: argparse.Namespace) -> int:
    checklist = Path(args.checklist)
    if not checklist.exists():
        print(f"ERROR: checklist not found: {checklist}")
        return 1
    lines = checklist.read_text(encoding="utf-8").splitlines()
    checked = sum(1 for line in lines if "- [x]" in line or "- [X]" in line)
    unchecked = sum(1 for line in lines if "- [ ]" in line)
    print(f"Checklist {checklist.name}: {checked} checked, {unchecked} unchecked")
    for line in lines:
        if "- [ ]" in line:
            print(f"  MISSING: {line.strip()}")
    if args.all and unchecked > 0:
        print("Gate failed: --all required but unchecked items remain")
        return 1
    return 0


def cmd_agent(args: argparse.Namespace) -> int:
    claimed = [f.strip() for f in args.claimed_files.split(",") if f.strip()]
    verifier = AgentVerifier(project_dir=args.project)
    result = verifier.verify_agent_task(args.task, claimed)
    print(f"[{('PASS' if result.passed else 'FAIL')}] {result.name}")
    if result.output:
        print(f"  diff: {result.output[:500]}")
    print(f"  reason: {result.reason}")
    return 0 if result.passed else 1


def cmd_all(args: argparse.Namespace) -> int:
    engine = _engine(args)
    project_type = args.type or VerificationEngine.detect_project_type(args.project)
    print(f"Detected project type: {project_type} (phase: {args.phase})")
    steps = template_lib.get_verification_commands(project_type, args.phase)
    if not steps:
        print(f"No verification steps defined for {project_type}/{args.phase}")
        return 0
    rendered_steps = [template_lib.render_step(step, args.project) for step in steps]
    if args.override:
        results = engine.run_with_override(rendered_steps, args.override)
        print(f"WARNING: Emergency override applied: {args.override}")
    else:
        results = engine.run_all(rendered_steps)
    for result in results:
        status = "PASS" if result.passed else ("OVERRIDE" if args.override else "FAIL")
        print(f"[{status}] {result.name}: {result.command}")
        if not result.passed:
            print(f"       reason: {result.reason}")
    failed = sum(1 for r in results if not r.passed)
    print(f"Summary: {len(results) - failed}/{len(results)} passed")
    if args.gate and not args.override and failed > 0:
        return 1
    return 0


def cmd_history(args: argparse.Namespace) -> int:
    engine = _engine(args)
    period = int(args.period.rstrip("d")) if args.period.endswith("d") else int(args.period)
    entries = engine.get_history(period)
    print(f"Verification history: {len(entries)} entries in last {period} days")
    for entry in entries[-10:]:
        status = "PASS" if entry.get("passed") else "FAIL"
        print(f"  {entry.get('timestamp', '?')} [{status}] {entry.get('name', '?')} ({entry.get('duration', 0.0)}s)")
    if args.stats:
        report = engine.compliance_report(period)
        print(f"Passed: {report.passed}/{report.total} ({report.passed_rate:.1%})")
        print(f"False completion rate: {report.false_completion_rate:.1%}")
        print(f"Avg verification time: {report.avg_verification_time}s")
        print(f"Most common failures: {', '.join(report.most_common_failures) or 'none'}")
        print(f"Emergency overrides: {report.emergency_overrides}")
    return 0


def cmd_coach(args: argparse.Namespace) -> int:
    guidance = {
        "strict": (
            "Strict mode: no completion claim without fresh verification evidence.\n"
            "Before claiming: 1) identify the proving command  2) run it fully\n"
            "3) read output + exit code  4) confirm it matches the claim  5) claim."
        ),
        "guided": (
            "Guided mode: pick the minimal verification that proves the claim.\n"
            "Tests pass -> run the test command. Build ok -> run the build.\n"
            "Never substitute a weaker check for the proving one."
        ),
        "permissive": (
            "Permissive mode: still record evidence for every claim, but allow\n"
            "partial verification with explicit 'unverified' labels on the claim."
        ),
    }
    print(guidance.get(args.mode, guidance["strict"]))
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.action == "tests":
        sys.exit(_run_command_step(args, args.expect))
    elif args.action == "build":
        sys.exit(_run_command_step(args, "pass"))
    elif args.action == "linter":
        sys.exit(_run_command_step(args, "pass"))
    elif args.action == "requirements":
        sys.exit(cmd_requirements(args))
    elif args.action == "agent":
        sys.exit(cmd_agent(args))
    elif args.action == "all":
        sys.exit(cmd_all(args))
    elif args.action == "history":
        sys.exit(cmd_history(args))
    elif args.action == "coach":
        sys.exit(cmd_coach(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
