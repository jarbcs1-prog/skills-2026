#!/usr/bin/env python3
"""CLI for the writing-skills skill.

Scaffolds, tests, validates, publishes, installs and composes skills.
All commands operate on skill directories with a SKILL.md at their root.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import scaffolder
from .registry import SkillRegistry
from .test_harness import SkillTestHarness, suggestion_for_uncovered
from .validator import SkillValidator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="writing-skills",
        description="Skill scaffolding, testing, validation and registry",
    )
    subparsers = parser.add_subparsers(dest="action", help="Available commands")
    subparsers.required = True

    init = subparsers.add_parser("init", help="Scaffold a new skill from a template")
    init.add_argument("--name", required=True, help="Skill name (kebab-case)")
    init.add_argument("--template", required=True, choices=list(scaffolder.TEMPLATES), help="Skill template")
    init.add_argument("--description", default="", help="Triggering-condition description")
    init.add_argument("--author", default="", help="Author name")
    init.add_argument("--version", default="1.0.0", help="Initial semantic version")
    init.add_argument("--dependencies", default="", help="Comma-separated dependency skill names")
    init.add_argument("--output", default=".", help="Parent directory for the new skill")

    test = subparsers.add_parser("test", help="Run the RED-GREEN-REFACTOR harness")
    test.add_argument("--skill", required=True, help="Path to the skill directory")
    test.add_argument("--full-cycle", action="store_true", help="Run RED + GREEN + REFACTOR")
    test.add_argument("--red-only", action="store_true", help="Run only the RED baseline phase")
    test.add_argument("--green-only", action="store_true", help="Run only the GREEN coverage phase")

    validate = subparsers.add_parser("validate", help="Validate skill structure")
    validate.add_argument("--skill", required=True, help="Path to the skill directory")
    validate.add_argument("--strict", action="store_true", help="Fail if score < 70")

    publish = subparsers.add_parser("publish", help="Publish a skill to a registry")
    publish.add_argument("--skill", required=True, help="Path to the skill directory")
    publish.add_argument("--version", default="", help="Version to publish (default: skill.yaml)")
    publish.add_argument("--registry", default="./registry", help="Registry directory")

    install = subparsers.add_parser("install", help="Install a skill from a registry")
    install.add_argument("spec", help="Skill spec: name or name@version")
    install.add_argument("--registry", default="./registry", help="Registry directory")
    install.add_argument("--target", default=".", help="Install destination directory")

    upgrade = subparsers.add_parser("upgrade", help="Upgrade an installed skill to a version")
    upgrade.add_argument("name", help="Installed skill name")
    upgrade.add_argument("--version", required=True, help="Target version")
    upgrade.add_argument("--registry", default="./registry", help="Registry directory")
    upgrade.add_argument("--target", default=".", help="Directory containing the installed skill")

    health = subparsers.add_parser("health", help="Report skill quality health")
    health.add_argument("--skill", required=True, help="Path to the skill directory")
    health.add_argument("--period", default="30d", help="Reporting period (unused placeholder)")

    compose = subparsers.add_parser("compose", help="Compose skills into a workflow")
    compose.add_argument("--skills", required=True, help="Comma-separated skill directories")
    compose.add_argument("--name", required=True, help="Workflow name (kebab-case)")
    compose.add_argument("--output", default=".", help="Parent directory for the workflow")

    return parser


def cmd_init(args: argparse.Namespace) -> int:
    dependencies = [d.strip() for d in args.dependencies.split(",") if d.strip()]
    try:
        root = scaffolder.SkillScaffolder().create(
            name=args.name,
            template=args.template,
            target_dir=Path(args.output),
            description=args.description,
            author=args.author,
            version=args.version,
            dependencies=dependencies,
        )
    except (scaffolder.SkillNameError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Created {args.template} skill: {root}")
    print(f"Next: python -m scripts.cli test --skill {root} --full-cycle")
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    try:
        harness = SkillTestHarness(Path(args.skill))
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 1

    if args.red_only:
        print(harness.run_red_phase().summary())
        return 0
    if args.green_only:
        report = harness.run_green_phase()
        print(report.summary())
        print()
        print(suggestion_for_uncovered(harness.skill_type, report.uncovered))
        return 0 if report.passed else 1
    if args.full_cycle:
        report = harness.run_full_cycle()
        print(report.summary())
        if not report.skilled.passed:
            print()
            print(suggestion_for_uncovered(harness.skill_type, report.skilled.uncovered))
        return 0 if report.passed else 1

    red = harness.run_red_phase()
    green = harness.run_green_phase()
    print(red.summary())
    print()
    print(green.summary())
    if not green.passed:
        print()
        print(suggestion_for_uncovered(harness.skill_type, green.uncovered))
    return 0 if green.passed else 1


def cmd_validate(args: argparse.Namespace) -> int:
    result = SkillValidator().validate(Path(args.skill), strict=args.strict)
    for error in result.errors:
        print(f"  ERROR: {error}")
    for warning in result.warnings:
        print(f"  WARN:  {warning}")
    print(result.summary())
    return 0 if result.valid else 1


def cmd_publish(args: argparse.Namespace) -> int:
    registry = SkillRegistry(Path(args.registry))
    result = registry.publish(Path(args.skill), version=args.version or None)
    print(result.summary())
    return 0 if result.published else 1


def cmd_install(args: argparse.Namespace) -> int:
    registry = SkillRegistry(Path(args.registry))
    try:
        result = registry.install(args.spec, Path(args.target))
    except (scaffolder.SkillNameError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(result.summary())
    return 0 if result.installed else 1


def cmd_upgrade(args: argparse.Namespace) -> int:
    registry = SkillRegistry(Path(args.registry))
    try:
        result = registry.upgrade(args.name, args.version, Path(args.target))
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1
    print(result.summary())
    return 0 if result.installed else 1


def cmd_health(args: argparse.Namespace) -> int:
    skill_dir = Path(args.skill)
    harness = SkillTestHarness(skill_dir)
    result = SkillValidator().validate(skill_dir, strict=False)
    green = harness.run_green_phase()
    lines = [
        f"Skill: {skill_dir.name}",
        f"Type: {harness.skill_type}",
        f"Structure: {result.summary()}",
        f"Coverage: {green.compliance_rate:.0%} across {len(green.scenario_runs)} scenarios",
        f"Period: {args.period}",
    ]
    for issue in result.errors:
        lines.append(f"  ERROR: {issue}")
    for issue in result.warnings:
        lines.append(f"  WARN:  {issue}")
    for name in green.uncovered:
        lines.append(f"  UNCOVERED: {name}")
    print("\n".join(lines))
    return 0 if result.valid and green.passed else 1


def cmd_compose(args: argparse.Namespace) -> int:
    sources = [p.strip() for p in args.skills.split(",") if p.strip()]
    if not sources:
        print("ERROR: --skills must name at least one skill directory")
        return 1
    try:
        scaffolder.validate_name(args.name)
    except scaffolder.SkillNameError as exc:
        print(f"ERROR: {exc}")
        return 1

    root = Path(args.output) / args.name
    if root.exists():
        print(f"ERROR: workflow directory already exists: {root}")
        return 1
    root.mkdir(parents=True)
    (root / "references").mkdir()

    parts = [
        "---",
        f"name: {args.name}",
        f"description: Use when executing the composed workflow that chains: {', '.join(sources)}",
        "---",
        "",
        f"# {args.name.replace('-', ' ').title()}",
        "",
        "## Composed Skills",
        "",
    ]
    for index, source in enumerate(sources, start=1):
        parts.append(f"### {index}. {source}")
        skill_dir = Path(source)
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            parts.append(f"Skill at: {skill_dir}")
            parts.append("")
            continue
        parts.append(f"(missing SKILL.md at {skill_dir})")
        parts.append("")
    parts.extend(
        [
            "## Execution Order",
            "",
            "1. Execute each skill in the order above.",
            "2. Confirm each skill's exit criteria before proceeding.",
            "3. If a gate fails, stop and report.",
            "",
            "## Verification",
            "",
            "This workflow is only verified when every composed skill passes its own",
            "test cycle (`python -m scripts.cli test --skill <skill> --full-cycle`).",
            "",
        ]
    )
    (root / "SKILL.md").write_text("\n".join(parts), encoding="utf-8")
    print(f"Composed workflow: {root}")
    print(f"References {len(sources)} skills in order.")
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.action == "init":
        sys.exit(cmd_init(args))
    elif args.action == "test":
        sys.exit(cmd_test(args))
    elif args.action == "validate":
        sys.exit(cmd_validate(args))
    elif args.action == "publish":
        sys.exit(cmd_publish(args))
    elif args.action == "install":
        sys.exit(cmd_install(args))
    elif args.action == "upgrade":
        sys.exit(cmd_upgrade(args))
    elif args.action == "health":
        sys.exit(cmd_health(args))
    elif args.action == "compose":
        sys.exit(cmd_compose(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
