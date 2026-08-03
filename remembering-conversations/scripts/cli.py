from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.conversation_index import ConversationIndex, tokenize
from scripts.pattern_detector import PatternDetector


def _index(cache: str | None) -> ConversationIndex:
    return ConversationIndex(Path(cache) if cache else None)


def _fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def cmd_search(args: argparse.Namespace) -> None:
    index = _index(args.cache)
    results = index.search(args.query, since=args.since, top_k=args.top)
    print(json.dumps({"query": args.query, "results": results}, ensure_ascii=False))


def cmd_patterns(args: argparse.Namespace) -> None:
    detector = PatternDetector(_index(args.cache))
    if args.type == "architectural":
        patterns = detector.detect_architectural_patterns(top_k=args.top)
    else:
        patterns = detector.detect_recurring_decisions(top_k=args.top)
    print(json.dumps({"type": args.type, "patterns": patterns}, ensure_ascii=False))


def cmd_similar(args: argparse.Namespace) -> None:
    detector = PatternDetector(_index(args.cache))
    results = detector.find_similar_situation(args.context, top_k=args.top)
    print(json.dumps({"context": args.context, "results": results}, ensure_ascii=False))


def cmd_sync(args: argparse.Namespace) -> None:
    export_dir = Path(args.export_dir)
    if not export_dir.is_dir():
        _fail(f"error: export dir not found: {export_dir}")
    index = _index(args.cache)
    try:
        imported = index.sync(export_dir)
    except FileNotFoundError:
        _fail(f"error: export dir not found: {export_dir}")
    print(
        json.dumps(
            {"export_dir": str(export_dir), "imported": imported, "total": len(index.all_ids())},
            ensure_ascii=False,
        )
    )


def cmd_summarize(args: argparse.Namespace) -> None:
    index = _index(args.cache)
    conversation = index.get(args.conversation_id)
    if conversation is None:
        _fail(f"error: conversation not found: {args.conversation_id}")
    print(
        json.dumps(
            {"conversation_id": args.conversation_id, "summary": conversation.get("summary", "")},
            ensure_ascii=False,
        )
    )


def cmd_add(args: argparse.Namespace) -> None:
    path = Path(args.conversation)
    if not path.is_file():
        _fail(f"error: conversation file not found: {path}")
    try:
        conversation = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        _fail(f"error: invalid conversation JSON: {path}")
    if not isinstance(conversation, dict):
        _fail(f"error: invalid conversation JSON: {path}")
    index = _index(args.cache)
    try:
        index.add(conversation)
    except ValueError as exc:
        _fail(f"error: {exc}")
    print(json.dumps({"conversation_id": conversation.get("conversation_id"), "added": True}, ensure_ascii=False))


def cmd_tags(args: argparse.Namespace) -> None:
    index = _index(args.cache)
    conversation = index.get(args.conversation_id)
    if conversation is None:
        _fail(f"error: conversation not found: {args.conversation_id}")
    new_tags = [tag.strip() for tag in args.add.split(",") if tag.strip()]
    existing = list(conversation.get("tags") or [])
    merged = existing + [tag for tag in new_tags if tag not in existing]
    conversation["tags"] = merged
    index.add(conversation)
    print(json.dumps({"conversation_id": args.conversation_id, "tags": merged}, ensure_ascii=False))


def cmd_export(args: argparse.Namespace) -> None:
    index = _index(args.cache)
    output = Path(args.output)
    if args.format == "json":
        data = {"conversations": [index.get(cid) for cid in index.all_ids()]}
        output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    elif args.format == "markdown":
        lines = ["# Conversation Archive", ""]
        for cid in index.all_ids():
            conversation = index.get(cid)
            if conversation is None:
                continue
            lines.append(f"## {cid}")
            lines.append("")
            lines.append(f"- **timestamp**: {conversation.get('timestamp', '')}")
            lines.append(f"- **tags**: {', '.join(conversation.get('tags') or [])}")
            lines.append(f"- **summary**: {conversation.get('summary', '')}")
            lines.append("")
            for message in conversation.get("messages", []):
                role = message.get("role", "")
                content = message.get("content", "")
                lines.append(f"**{role}**: {content}")
                lines.append("")
        output.write_text("\n".join(lines), encoding="utf-8")
    else:
        _fail(f"error: unknown format: {args.format}")
    print(json.dumps({"written": str(output)}, ensure_ascii=False))


def cmd_analytics(args: argparse.Namespace) -> None:
    index = _index(args.cache)
    days = 30
    period = args.period or "30d"
    if period.endswith("d") and period[:-1].isdigit():
        days = int(period[:-1])
    conversation_ids = index.recent(days=days)
    total_messages = 0
    unique_terms: set[str] = set()
    for cid in conversation_ids:
        conversation = index.get(cid)
        if conversation is None:
            continue
        total_messages += len(conversation.get("messages", []))
        for message in conversation.get("messages", []):
            unique_terms.update(tokenize(message.get("content", "")))
    print(
        json.dumps(
            {
                "conversations": len(conversation_ids),
                "total_messages": total_messages,
                "unique_terms": len(unique_terms),
                "top_queries": index.top_queries(limit=5),
            },
            ensure_ascii=False,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="remembering-conversations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="hybrid search over indexed conversations")
    search.add_argument("query")
    search.add_argument("--since")
    search.add_argument("--top", type=int, default=10)
    search.add_argument("--cache")
    search.set_defaults(func=cmd_search)

    patterns = subparsers.add_parser("patterns", help="detect recurring patterns")
    patterns.add_argument("--type", choices=["decisions", "architectural"], default="decisions")
    patterns.add_argument("--top", type=int, default=10)
    patterns.add_argument("--cache")
    patterns.set_defaults(func=cmd_patterns)

    similar = subparsers.add_parser("similar", help="find similar past situations")
    similar.add_argument("--context", required=True)
    similar.add_argument("--top", type=int, default=5)
    similar.add_argument("--cache")
    similar.set_defaults(func=cmd_similar)

    sync = subparsers.add_parser("sync", help="import episodic-memory exports")
    sync.add_argument("--export-dir", required=True)
    sync.add_argument("--cache")
    sync.set_defaults(func=cmd_sync)

    summarize = subparsers.add_parser("summarize", help="show a conversation summary")
    summarize.add_argument("--conversation-id", required=True)
    summarize.add_argument("--cache")
    summarize.set_defaults(func=cmd_summarize)

    add = subparsers.add_parser("add", help="add a single conversation")
    add.add_argument("--conversation", required=True)
    add.add_argument("--cache")
    add.set_defaults(func=cmd_add)

    tags = subparsers.add_parser("tags", help="append tags to a conversation")
    tags.add_argument("--add", required=True)
    tags.add_argument("--conversation-id", required=True)
    tags.add_argument("--cache")
    tags.set_defaults(func=cmd_tags)

    export = subparsers.add_parser("export", help="dump the index to a file")
    export.add_argument("--format", default="markdown")
    export.add_argument("--output", required=True)
    export.add_argument("--cache")
    export.set_defaults(func=cmd_export)

    analytics = subparsers.add_parser("analytics", help="index usage analytics")
    analytics.add_argument("--period", default="30d")
    analytics.add_argument("--cache")
    analytics.set_defaults(func=cmd_analytics)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
