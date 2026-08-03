"""Command-line interface for the skill-creator toolkit.

Commands:
  init      Scaffold a new skill from a template
  validate  Validate a skill directory
  publish   Publish a skill into a local registry
  install   Install a skill from a local registry
  deps      Resolve a skill's dependencies
  optimize  Optimize a skill description against trigger evals
"""

from __future__ import annotations

import argparse
import json
import sys

from scripts.init_skill import SkillNameError, SkillScaffolder
from scripts.registry import SkillRegistry
from scripts.templates import TEMPLATE_NAMES, describe_templates
from scripts.validate_skill import validate_skill


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skill-creator")
    subparsers = parser.add_subparsers(dest="action", required=True)

    init_parser = subparsers.add_parser("init", help="scaffold a new skill")
    init_parser.add_argument("--name", required=True)
    init_parser.add_argument("--template", required=True, choices=TEMPLATE_NAMES)
    init_parser.add_argument("--description", default="")
    init_parser.add_argument("--author", default="unknown")
    init_parser.add_argument("--version", default="1.0.0")
    init_parser.add_argument("--dependencies", default="")
    init_parser.add_argument("--output", default=".")

    validate_parser = subparsers.add_parser("validate", help="validate a skill")
    validate_parser.add_argument("--skill", required=True)
    validate_parser.add_argument("--strict", action="store_true")

    publish_parser = subparsers.add_parser("publish", help="publish to a registry")
    publish_parser.add_argument("--skill", required=True)
    publish_parser.add_argument("--registry", default="./registry")
    publish_parser.add_argument("--version")

    install_parser = subparsers.add_parser("install", help="install from a registry")
    install_parser.add_argument("spec")
    install_parser.add_argument("--registry", default="./registry")
    install_parser.add_argument("--target", default=".")

    deps_parser = subparsers.add_parser("deps", help="resolve dependencies")
    deps_parser.add_argument("--skill", required=True)
    deps_parser.add_argument("--registry", default="./registry")

    optimize_parser = subparsers.add_parser("optimize", help="optimize a description")
    optimize_parser.add_argument("--skill", required=True)
    optimize_parser.add_argument("--eval-set", required=True)
    optimize_parser.add_argument("--model", required=True)
    optimize_parser.add_argument("--max-iterations", type=int, default=5)
    optimize_parser.add_argument("--holdout", type=float, default=0.4)
    optimize_parser.add_argument("--results-dir")

    templates_parser = subparsers.add_parser("templates", help="list templates")
    templates_parser.add_argument("--describe", action="store_true")

    return parser


def _cmd_init(args: argparse.Namespace) -> int:
    dependencies = [d.strip() for d in args.dependencies.split(",") if d.strip()]
    try:
        root = SkillScaffolder().create(
            args.name,
            args.template,
            target_dir=args.output,
            description=args.description,
            author=args.author,
            version=args.version,
            dependencies=dependencies,
        )
    except (SkillNameError, FileExistsError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"Created skill at {root}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    result = validate_skill(args.skill)
    print(result.render())
    if result.valid and args.strict and result.score < 70:
        print("ERROR: strict validation requires score >= 70")
        return 1
    return 0 if result.valid else 1


def _cmd_publish(args: argparse.Namespace) -> int:
    result = SkillRegistry(args.registry).publish(args.skill, args.version)
    print(result.summary())
    return 0 if result.published else 1


def _cmd_install(args: argparse.Namespace) -> int:
    result = SkillRegistry(args.registry).install(args.spec, args.target)
    print(result.summary())
    return 0 if result.installed else 1


def _cmd_deps(args: argparse.Namespace) -> int:
    try:
        ordered = SkillRegistry(args.registry).resolve_dependencies(args.skill)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1
    if not ordered:
        print("No dependencies.")
        return 0
    for i, name in enumerate(ordered, start=1):
        print(f"{i}. {name}")
    return 0


def _cmd_optimize(args: argparse.Namespace) -> int:
    from scripts.optimize_description import DescriptionOptimizer

    try:
        result = DescriptionOptimizer(args.model).optimize(
            args.skill,
            args.eval_set,
            max_iterations=args.max_iterations,
            holdout=args.holdout,
            results_dir=args.results_dir,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(result.summary())
    if result.data:
        print(json.dumps(result.data, indent=2))
    return 0 if result.optimized else 1


def _cmd_templates(args: argparse.Namespace) -> int:
    print(", ".join(TEMPLATE_NAMES))
    if args.describe:
        print()
        print(describe_templates())
    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    handlers = {
        "init": _cmd_init,
        "validate": _cmd_validate,
        "publish": _cmd_publish,
        "install": _cmd_install,
        "deps": _cmd_deps,
        "optimize": _cmd_optimize,
        "templates": _cmd_templates,
    }
    handler = handlers.get(args.action)
    if handler is None:
        parser.print_help()
        sys.exit(1)
    sys.exit(handler(args))


if __name__ == "__main__":
    main()
