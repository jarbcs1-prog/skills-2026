#!/usr/bin/env python3
"""CLI for dynamic-context-pruning skill."""
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Dynamic context pruning and management tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    monitor = subparsers.add_parser("monitor", help="Monitor context thresholds")
    monitor.add_argument("--config", default=".agent_context_config.json")

    compact = subparsers.add_parser("compact", help="Compact context")
    compact.add_argument("--context", required=True)
    compact.add_argument("--output", default="compacted.json")

    summarize = subparsers.add_parser("summarize", help="Summarize context")
    summarize.add_argument("--context", required=True)
    summarize.add_argument("--schema", default="agent_default")

    offload = subparsers.add_parser("offload", help="Offload context data")
    offload.add_argument("--data", required=True)
    offload.add_argument("--metadata", required=True)

    kv_cache = subparsers.add_parser("kv-cache", help="Validate/fix KV-cache")
    kv_cache.add_argument("--validate", action="store_true")
    kv_cache.add_argument("--fix", action="store_true")
    kv_cache.add_argument("--context", default="")

    thresholds = subparsers.add_parser("thresholds", help="Manage thresholds")
    thresholds.add_argument("--show", action="store_true")
    thresholds.add_argument("--update", action="store_true")
    thresholds.add_argument("--config", default=".agent_context_config.json")

    args = parser.parse_args()

    if args.command == "monitor":
        print(f"Monitoring context with config: {args.config}")
    elif args.command == "compact":
        print(f"Compacting context: {args.context} -> {args.output}")
    elif args.command == "summarize":
        print(f"Summarizing context: {args.context} (schema: {args.schema})")
    elif args.command == "offload":
        print(f"Offloading data: {args.data} with metadata: {args.metadata}")
    elif args.command == "kv-cache":
        action = "validate" if args.validate else ("fix" if args.fix else "check")
        print(f"KV-cache {action} for context: {args.context or 'default'}")
    elif args.command == "thresholds":
        if args.show:
            print("Showing current thresholds")
        elif args.update:
            print(f"Updating thresholds in {args.config}")
        else:
            print("Use --show or --update with thresholds command")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()