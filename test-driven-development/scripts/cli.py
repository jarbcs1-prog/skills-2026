#!/usr/bin/env python3
"""CLI for test-driven-development skill."""
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="TDD enforcement and scaffolding tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    new = subparsers.add_parser("new", help="Scaffold a new test and implementation")
    new.add_argument("--feature", required=True, help="Feature description")
    new.add_argument("--language", default="python", choices=["python", "javascript", "rust", "go", "java"])
    new.add_argument("--output", default="", help="Output directory")

    red = subparsers.add_parser("red", help="Run test in RED phase")
    red.add_argument("--test", required=True, help="Test to run")

    green = subparsers.add_parser("green", help="Run test in GREEN phase")
    green.add_argument("--implement", required=True, help="Implementation file")

    refactor = subparsers.add_parser("refactor", help="Run refactor phase")
    refactor.add_argument("--clean", required=True, help="File to refactor")

    cycle = subparsers.add_parser("cycle", help="Run full RED-GREEN-REFACTOR cycle")
    cycle.add_argument("--test", required=True)
    cycle.add_argument("--implement", required=True)

    verify = subparsers.add_parser("verify", help="Verify TDD compliance")
    verify.add_argument("--coverage", type=int, default=80)
    verify.add_argument("--mutation", action="store_true")

    coach = subparsers.add_parser("coach", help="TDD coaching mode")
    coach.add_argument("--mode", default="strict", choices=["strict", "guided", "permissive"])
    coach.add_argument("--language", default="python")

    stats = subparsers.add_parser("stats", help="Show TDD statistics")
    stats.add_argument("--project", default=".")
    stats.add_argument("--period", default="30d")

    args = parser.parse_args()

    if args.command == "new":
        print(f"Scaffolding {args.feature} in {args.language}")
    elif args.command == "red":
        print(f"Running RED test: {args.test}")
    elif args.command == "green":
        print(f"Running GREEN implementation: {args.implement}")
    elif args.command == "refactor":
        print(f"Running REFACTOR on: {args.clean}")
    elif args.command == "cycle":
        print(f"Running TDD cycle: {args.test} -> {args.implement}")
    elif args.command == "verify":
        print(f"Verifying coverage >= {args.coverage}%, mutation={'on' if args.mutation else 'off'}")
    elif args.command == "coach":
        print(f"Coach mode ({args.mode}) for {args.language}")
    elif args.command == "stats":
        print(f"TDD stats for {args.project} over {args.period}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()