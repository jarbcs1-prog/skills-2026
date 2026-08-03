#!/usr/bin/env python3
"""CLI for project-planner skill."""
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Project planning tool with templates, scheduling, and tracking"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    init = subparsers.add_parser("init", help="Initialize a new project plan")
    init.add_argument("--template", default="web_app",
                      choices=["web_app", "mobile_app", "api_service", "cli_tool",
                               "library", "data_pipeline", "ml_project", "migration",
                               "refactor", "security_audit"])
    init.add_argument("--name", required=True, help="Project name")
    init.add_argument("--output", default="", help="Output file path")

    generate = subparsers.add_parser("generate", help="Generate a project plan")
    generate.add_argument("--template", required=True)
    generate.add_argument("--name", required=True)
    generate.add_argument("--output", default="", help="Output file path")

    schedule = subparsers.add_parser("schedule", help="Calculate schedule and critical path")
    schedule.add_argument("--plan", required=True, help="Plan file path")
    schedule.add_argument("--critical-path", action="store_true")

    track = subparsers.add_parser("track", help="Track project progress")
    track.add_argument("--plan", required=True)
    track.add_argument("--update", default="", help="Task update (task-id:status)")

    report = subparsers.add_parser("report", help="Generate project report")
    report.add_argument("--plan", required=True)
    report.add_argument("--format", default="burndown",
                        choices=["burndown", "variance", "milestone"])
    report.add_argument("--output", default="", help="Output file path")

    export = subparsers.add_parser("export", help="Export plan to external format")
    export.add_argument("--plan", required=True)
    export.add_argument("--format", default="markdown",
                        choices=["markdown", "github-projects", "jira", "notion"])
    export.add_argument("--output", default="", help="Output file path")

    replan = subparsers.add_parser("replan", help="Replan with changes")
    replan.add_argument("--plan", required=True)
    replan.add_argument("--changes", required=True, help="Changes JSON file")

    args = parser.parse_args()

    if args.command == "init":
        print(f"Initializing project '{args.name}' with template '{args.template}'")
    elif args.command == "generate":
        print(f"Generating plan for '{args.name}' using template '{args.template}'")
    elif args.command == "schedule":
        print(f"Scheduling plan from {args.plan}"
              + (" with critical path calculation" if args.critical_path else ""))
    elif args.command == "track":
        print(f"Tracking plan from {args.plan}"
              + (f" with update: {args.update}" if args.update else ""))
    elif args.command == "report":
        print(f"Generating {args.format} report from {args.plan}")
    elif args.command == "export":
        print(f"Exporting plan from {args.plan} to {args.format} format")
    elif args.command == "replan":
        print(f"Replanning {args.plan} with changes from {args.changes}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()