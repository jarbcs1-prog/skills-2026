#!/usr/bin/env python3
"""CLI for having-difficult-conversations skill."""
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Difficult conversation preparation and practice tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    prepare = subparsers.add_parser("prepare", help="Prepare for a difficult conversation")
    prepare.add_argument("--type", required=True, choices=[
        "feedback", "performance", "termination", "conflict", "negotiation",
        "complaint", "boundary", "escalation", "layoff", "restructuring"
    ])
    prepare.add_argument("--person", default="")
    prepare.add_argument("--output", default="", help="Output file path")

    template = subparsers.add_parser("template", help="Get a conversation template")
    template.add_argument("--type", required=True, choices=[
        "feedback", "performance", "termination", "conflict", "negotiation"
    ])
    template.add_argument("--format", default="markdown", choices=["markdown", "pdf"])

    practice = subparsers.add_parser("practice", help="Practice a conversation type")
    practice.add_argument("--type", required=True)
    practice.add_argument("--scenario", default="")

    simulate = subparsers.add_parser("simulate", help="Simulate a conversation")
    simulate.add_argument("--persona", default="defensive", choices=[
        "defensive", "denial", "emotional", "agreeable", "hostile"
    ])
    simulate.add_argument("--opening", default="")

    log = subparsers.add_parser("log", help="Log a conversation outcome")
    log.add_argument("--outcome", required=True, choices=[
        "resolved", "partial", "unresolved", "escalated"
    ])
    log.add_argument("--followup", default="")
    log.add_argument("--person", default="")

    history = subparsers.add_parser("history", help="View conversation history")
    history.add_argument("--person", default="")
    history.add_argument("--last", type=int, default=10)

    analytics = subparsers.add_parser("analytics", help="View conversation analytics")
    analytics.add_argument("--month", default="")
    analytics.add_argument("--metrics", nargs="+", default=["resolution", "relationship"])

    args = parser.parse_args()

    if args.command == "prepare":
        print(f"Preparing {args.type} conversation with {args.person or 'unknown person'}")
        print("Use the preparation template to structure your approach.")
    elif args.command == "template":
        print(f"Generating {args.type} template in {args.format} format")
    elif args.command == "practice":
        print(f"Practicing {args.type} conversation")
    elif args.command == "simulate":
        print(f"Simulating conversation with {args.persona} persona")
    elif args.command == "log":
        print(f"Logging outcome: {args.outcome}")
    elif args.command == "history":
        print(f"Showing last {args.last} conversations")
    elif args.command == "analytics":
        print(f"Showing analytics for {args.month or 'all time'}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()