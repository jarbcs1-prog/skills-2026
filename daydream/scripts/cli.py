from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from .daydream_config import DEFAULT_CONFIG, load_config
from .dedup import SemanticDeduplicator
from .graph import InsightGraph
from .notes import load_notes, sample_pairs
from .quality import critique
from .synthesizer import synthesize_insight


def _history_path(base: Path, config: dict[str, Any]) -> Path:
    return base / config["output"]["history_file"]


def _read_history(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"runs": [], "insights": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"runs": [], "insights": []}
    if not isinstance(data, dict):
        return {"runs": [], "insights": []}
    data.setdefault("runs", [])
    data.setdefault("insights", [])
    return data


def _write_history(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _render_insight(insight: dict[str, Any], timestamp: str) -> str:
    scores = insight.get("scores", {})
    sources = insight["sources"]
    header = "\n".join(
        [
            "---",
            f"created_date: '{timestamp}'",
            "type: daydream",
            "source_notes:",
            f"  - '{sources[0]}'",
            f"  - '{sources[1]}'",
            "scores:",
            f"  novelty: {scores.get('novelty', 0.0):.2f}",
            f"  actionability: {scores.get('actionability', 0.0):.2f}",
            f"  connectivity: {scores.get('connectivity', 0.0):.2f}",
            f"  evidence: {scores.get('evidence', 0.0):.2f}",
            f"  weighted: {scores.get('weighted', 0.0):.2f}",
            "---",
        ]
    )
    return f"{header}\n\n# {insight['title']}\n\n{insight['text']}\n"


def cmd_run(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    if args.pairs is not None:
        config["sampling"]["pairs_per_run"] = args.pairs
    base = Path.cwd()
    vault = Path(args.vault) if args.vault is not None else Path(config["vault"]["path"])
    notes = load_notes(vault, config)
    pairs = sample_pairs(notes, config["sampling"]["pairs_per_run"], args.seed)

    generated = [synthesize_insight(note_a, note_b) for note_a, note_b in pairs]
    dimensions = config["dimensions"]
    threshold = config["quality"]["threshold"]

    passed: list[dict[str, Any]] = []
    for (note_a, note_b), insight in zip(pairs, generated, strict=True):
        result = critique(insight["text"], note_a["text"], note_b["text"], dimensions, threshold)
        insight["scores"] = result["scores"]
        if result["passed"]:
            passed.append(insight)

    history = _read_history(_history_path(base, config))
    deduper = SemanticDeduplicator()
    kept: list[dict[str, Any]] = []
    dedup_count = 0
    known_texts = [entry.get("text", "") for entry in history.get("insights", []) if isinstance(entry, dict)]
    for insight in passed:
        if any(deduper.is_duplicate(insight["text"], known) for known in known_texts):
            dedup_count += 1
            continue
        if any(deduper.is_duplicate(insight["text"], existing["text"]) for existing in kept):
            dedup_count += 1
            continue
        kept.append(insight)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = base / config["output"]["insight_dir"]
    written = 0
    if not args.dry_run and kept:
        output_dir.mkdir(parents=True, exist_ok=True)
        body = "\n\n---\n\n".join(_render_insight(insight, timestamp) for insight in kept)
        (output_dir / f"{timestamp}.md").write_text(body + "\n", encoding="utf-8")
        written = len(kept)
        history["runs"].append(
            {
                "date": timestamp,
                "notes_loaded": len(notes),
                "pairs_sampled": len(pairs),
                "insights_generated": len(generated),
                "insights_passed": len(passed),
                "insights_written": written,
            }
        )
        for insight in kept:
            history["insights"].append(
                {
                    "title": insight["title"],
                    "text": insight["text"],
                    "sources": insight["sources"],
                    "scores": insight.get("scores", {}),
                    "date": timestamp,
                }
            )
        _write_history(_history_path(base, config), history)

    print(
        json.dumps(
            {
                "vault": str(vault),
                "notes_loaded": len(notes),
                "pairs_sampled": len(pairs),
                "insights_generated": len(generated),
                "insights_passed": len(passed),
                "deduplicated": dedup_count,
                "written": written,
                "output_dir": str(output_dir),
            }
        )
    )


def cmd_config(args: argparse.Namespace) -> None:
    print(json.dumps(load_config(args.config)))


def cmd_dedup(args: argparse.Namespace) -> None:
    notes = load_notes(Path(args.vault), DEFAULT_CONFIG)
    deduper = SemanticDeduplicator(threshold=args.threshold)
    pairs = []
    for i in range(len(notes)):
        for j in range(i + 1, len(notes)):
            similarity = deduper.similarity(notes[i]["text"], notes[j]["text"])
            if similarity >= args.threshold:
                pairs.append(
                    {"a": notes[i]["title"], "b": notes[j]["title"], "similarity": round(similarity, 4)}
                )
    pairs.sort(key=lambda pair: (-pair["similarity"], pair["a"], pair["b"]))
    print(json.dumps({"pairs": pairs}))


def cmd_graph(args: argparse.Namespace) -> None:
    base = Path.cwd()
    notes = load_notes(Path(args.vault), DEFAULT_CONFIG)
    history = _read_history(_history_path(base, DEFAULT_CONFIG))
    insights = [entry for entry in history.get("insights", []) if isinstance(entry, dict)]
    graph = InsightGraph(notes, insights)
    export = Path(args.export) if args.export else base / DEFAULT_CONFIG["output"]["graph_file"]
    graph.export_graphml(export)
    print(
        json.dumps(
            {
                "notes": len(notes),
                "edges": len(graph.edges()),
                "communities": len(graph.communities()),
                "export": str(export),
            }
        )
    )


def cmd_stats(args: argparse.Namespace) -> None:
    base = Path.cwd()
    history = _read_history(_history_path(base, DEFAULT_CONFIG))
    insights = [entry for entry in history.get("insights", []) if isinstance(entry, dict)]
    scores = [
        float(entry["scores"]["weighted"])
        for entry in insights
        if isinstance(entry.get("scores"), dict) and "weighted" in entry["scores"]
    ]
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0
    print(
        json.dumps(
            {
                "runs": len(history.get("runs", [])),
                "total_insights": len(insights),
                "avg_score": avg_score,
            }
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="daydream", description="Vault daydream skill CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Run a daydream session")
    p_run.add_argument("--vault", default=None)
    p_run.add_argument("--pairs", type=int, default=None)
    p_run.add_argument("--config", default=None)
    p_run.add_argument("--seed", type=int, default=None)
    p_run.add_argument("--dry-run", action="store_true")
    p_run.set_defaults(func=cmd_run)

    p_config = sub.add_parser("config", help="Configuration commands")
    config_sub = p_config.add_subparsers(dest="config_command", required=True)
    p_show = config_sub.add_parser("show", help="Show the effective configuration")
    p_show.add_argument("--config", default=None)
    p_show.set_defaults(func=cmd_config)

    p_dedup = sub.add_parser("dedup", help="Find near-duplicate notes")
    p_dedup.add_argument("--vault", required=True)
    p_dedup.add_argument("--threshold", type=float, default=0.85)
    p_dedup.set_defaults(func=cmd_dedup)

    p_graph = sub.add_parser("graph", help="Build the insight graph")
    p_graph.add_argument("--vault", required=True)
    p_graph.add_argument("--export", default=None)
    p_graph.set_defaults(func=cmd_graph)

    p_stats = sub.add_parser("stats", help="Show history statistics")
    p_stats.set_defaults(func=cmd_stats)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
