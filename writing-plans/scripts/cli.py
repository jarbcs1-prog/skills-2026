#!/usr/bin/env python3
"""CLI for writing-plans skill.

Scaffolds, validates, composes, versions and tracks implementation plans.
Plans are markdown documents parsed and serialized by scripts.plans.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from . import templates as template_lib
from .plans import Plan, PlanHeader, Task, load_plan, render_plan, save_plan
from .traceability import PlanTraceability
from .validator import PlanValidator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="writing-plans",
        description="Implementation plan scaffolding, validation and tracking",
    )
    subparsers = parser.add_subparsers(dest="action", help="Available commands")
    subparsers.required = True

    init = subparsers.add_parser("init", help="Scaffold a new plan from a template")
    init.add_argument("--template", required=True, choices=template_lib.TEMPLATE_NAMES, help="Plan template")
    init.add_argument("--name", required=True, help="Plan/feature name")
    init.add_argument("--goal", default="", help="One-sentence goal")
    init.add_argument("--tech-stack", default="", help="Key technologies/libraries")
    init.add_argument("--output", default=".", help="Output directory for the plan file")

    validate = subparsers.add_parser("validate", help="Validate a plan document")
    validate.add_argument("--plan", required=True, help="Path to the plan markdown file")
    validate.add_argument("--strict", action="store_true", help="Fail if score < 70")

    extract = subparsers.add_parser("extract-tasks", help="Extract tasks for execution")
    extract.add_argument("--plan", required=True, help="Path to the plan markdown file")
    extract.add_argument("--format", default="subagent", choices=["subagent", "simple"], help="Output format")

    compose = subparsers.add_parser("compose", help="Combine multiple plans into one")
    compose.add_argument("--plans", required=True, help="Comma-separated plan files")
    compose.add_argument("--name", required=True, help="Name of the composed plan")
    compose.add_argument("--output", default=".", help="Output directory")

    version = subparsers.add_parser("version", help="Bump the plan version")
    version.add_argument("--plan", required=True, help="Path to the plan markdown file")
    version.add_argument("--bump", default="patch", choices=["major", "minor", "patch"], help="Version bump type")

    track = subparsers.add_parser("track", help="Show or update task status")
    track.add_argument("--plan", required=True, help="Path to the plan markdown file")
    track.add_argument("--status", action="store_true", help="Print status summary")
    track.add_argument("--task", type=int, default=0, help="Task number to update")
    track.add_argument("--set", default="", choices=["pending", "in_progress", "done", "blocked", "cancelled"], help="Status to set")

    sync = subparsers.add_parser("sync", help="Link plan tasks to git commits and detect drift")
    sync.add_argument("--plan", required=True, help="Path to the plan markdown file")
    sync.add_argument("--project", default=".", help="Repository directory")
    sync.add_argument("--commits", action="store_true", help="Print traceability report")

    return parser


def _plan_filename(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "plan"
    from datetime import date

    return f"{date.today().isoformat()}-{slug}.md"


def cmd_init(args: argparse.Namespace) -> int:
    plan = template_lib.generate_plan(args.template, args.name, args.goal, args.tech_stack)
    target = Path(args.output) / _plan_filename(args.name)
    save_plan(plan, target)
    print(f"Created {args.template} plan: {target}")
    print(f"Validate it with: python -m scripts.cli validate --plan {target}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    plan = load_plan(args.plan)
    result = PlanValidator().validate(plan, strict=args.strict)
    print(f"Plan: {plan.header.name} (version {plan.header.version}, {len(plan.tasks)} tasks)")
    for error in result.errors:
        print(f"  ERROR: {error}")
    for warning in result.warnings:
        print(f"  WARN:  {warning}")
    print(result.summary())
    return 0 if result.valid else 1


def cmd_extract(args: argparse.Namespace) -> int:
    plan = load_plan(args.plan)
    print(f"Extracting {len(plan.tasks)} tasks from {args.plan}")
    for task in plan.tasks:
        if args.format == "subagent":
            print(f"--- Task {task.number}: {task.title} ---")
            print(task.objective)
            for path in task.files.get("create", []):
                print(f"  Create: {path}")
            for path in task.files.get("modify", []):
                print(f"  Modify: {path}")
            for path in task.files.get("test", []):
                print(f"  Test:   {path}")
        else:
            print(f"{task.number}\t{task.title}\t{task.status}")
    return 0


def cmd_compose(args: argparse.Namespace) -> int:
    sources = [p.strip() for p in args.plans.split(",") if p.strip()]
    if not sources:
        print("ERROR: --plans must name at least one plan")
        return 1
    plans = [load_plan(path) for path in sources]
    header = PlanHeader(
        name=args.name,
        goal="; ".join(p.header.goal for p in plans if p.header.goal),
        architecture="Composed from: " + ", ".join(sources),
        tech_stack="; ".join(p.header.tech_stack for p in plans if p.header.tech_stack),
        version="0.1.0",
    )
    tasks: list[Task] = []
    number = 1
    for plan in plans:
        for task in plan.tasks:
            task.number = number
            tasks.append(task)
            number += 1
    composed = Plan(header=header, tasks=tasks)
    target = Path(args.output) / _plan_filename(args.name)
    save_plan(composed, target)
    print(f"Composed {len(sources)} plans into {target} ({len(tasks)} tasks)")
    return 0


def cmd_version(args: argparse.Namespace) -> int:
    path = Path(args.plan)
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^\*\*Version:\*\*\s*([\w.\-]+)", text, re.MULTILINE)
    current = match.group(1) if match else "0.1.0"
    parts = [int(p) for p in current.split(".") if p.isdigit()][:3]
    while len(parts) < 3:
        parts.append(0)
    major, minor, patch = parts
    if args.bump == "major":
        major, minor, patch = major + 1, 0, 0
    elif args.bump == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1
    new_version = f"{major}.{minor}.{patch}"
    updated = re.sub(r"^\*\*Version:\*\*\s*[\w.\-]+", f"**Version:** {new_version}", text, flags=re.MULTILINE)
    path.write_text(updated, encoding="utf-8")
    print(f"Bumped version {current} -> {new_version} in {path}")
    return 0


def cmd_track(args: argparse.Namespace) -> int:
    path = Path(args.plan)
    plan = load_plan(args.plan)
    if args.task:
        task = plan.task_by_number(args.task)
        if task is None:
            print(f"ERROR: no task {args.task} in {path}")
            return 1
        task.status = args.set
        path.write_text(render_plan(plan), encoding="utf-8")
        print(f"Task {args.task} status -> {args.set}")
        return 0
    counts: dict[str, int] = {}
    for task in plan.tasks:
        counts[task.status] = counts.get(task.status, 0) + 1
        print(f"Task {task.number}: [{task.status}] {task.title}")
    print("Summary: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    plan = load_plan(args.plan)
    tracer = PlanTraceability(project_dir=args.project)
    missing = tracer.detect_drift(plan)
    for issue in missing:
        print(f"  DRIFT: {issue}")
    if args.commits:
        report = tracer.link_tasks_to_commits(plan)
        for link in report.links:
            status = "linked" if link.covered else "unlinked"
            print(f"Task {link.task_id}: {link.task_title} [{status}] {len(link.commits)} commits")
        print(report.summary())
    if missing:
        return 1
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.action == "init":
        sys.exit(cmd_init(args))
    elif args.action == "validate":
        sys.exit(cmd_validate(args))
    elif args.action == "extract-tasks":
        sys.exit(cmd_extract(args))
    elif args.action == "compose":
        sys.exit(cmd_compose(args))
    elif args.action == "version":
        sys.exit(cmd_version(args))
    elif args.action == "track":
        sys.exit(cmd_track(args))
    elif args.action == "sync":
        sys.exit(cmd_sync(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
