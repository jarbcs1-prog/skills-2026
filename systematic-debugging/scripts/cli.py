#!/usr/bin/env python3
"""CLI for systematic-debugging skill."""
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Systematic debugging workflow tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    start = subparsers.add_parser("start", help="Start a debugging session")
    start.add_argument("--error", default="", help="Error message")
    start.add_argument("--test", default="", help="Test command to reproduce")

    worksheet = subparsers.add_parser("worksheet", help="Generate debugging worksheet")
    worksheet.add_argument("--output", default="debug-worksheet.md", help="Output file")

    evidence = subparsers.add_parser("evidence", help="Log evidence")
    evidence.add_argument("--component", required=True)
    evidence.add_argument("--input", default="")
    evidence.add_argument("--output", default="")

    trace = subparsers.add_parser("trace", help="Trace a variable")
    trace.add_argument("--variable", required=True)
    trace.add_argument("--from", default="", dest="from_loc")

    hypothesis = subparsers.add_parser("hypothesis", help="Add a hypothesis")
    hypothesis.add_argument("--add", required=True)
    hypothesis.add_argument("--test", default="")

    pattern = subparsers.add_parser("pattern", help="Search bug patterns")
    pattern.add_argument("--search", required=True)
    pattern.add_argument("--language", default="python")

    report = subparsers.add_parser("report", help="Generate debug report")
    report.add_argument("--format", default="markdown", choices=["markdown", "html"])
    report.add_argument("--output", default="debug-report.md")

    args = parser.parse_args()

    if args.command == "start":
        print(f"Starting debug session for: {args.error or 'unknown error'}")
        if args.test:
            print(f"Reproduction test: {args.test}")
    elif args.command == "worksheet":
        print(f"Generating worksheet -> {args.output}")
    elif args.command == "evidence":
        print(f"Logging evidence for component: {args.component}")
    elif args.command == "trace":
        print(f"Tracing variable '{args.variable}' from {args.from_loc or 'unknown'}")
    elif args.command == "hypothesis":
        print(f"Adding hypothesis: {args.add}")
    elif args.command == "pattern":
        print(f"Searching patterns for '{args.search}' in {args.language}")
    elif args.command == "report":
        print(f"Generating {args.format} report -> {args.output}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()