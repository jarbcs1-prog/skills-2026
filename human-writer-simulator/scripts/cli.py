"""CLI for human-writer-simulator skill."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.detector import detect_ai_text
from scripts.scorer import score_human_likeness
from scripts.rewriter import HumanRewriter, RewriteConstraints


def _read_input(input_arg: str) -> str:
    path = Path(input_arg)
    if path.exists():
        return path.read_text()
    return input_arg


def cmd_detect(args: argparse.Namespace) -> int:
    text = _read_input(args.text)
    result = detect_ai_text(text)

    if args.detailed:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps({
            "ai_probability": result["ai_probability"],
            "is_ai_generated": result["is_ai_generated"],
            "indicators": result["indicators"],
        }, indent=2))
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    text = _read_input(args.text)
    style = args.style_profile or "conversational"
    result = score_human_likeness(text, style)

    print(json.dumps(result, indent=2))
    return 0


def cmd_rewrite(args: argparse.Namespace) -> int:
    text = _read_input(args.text)
    style = args.style or "conversational"
    imperfection = args.imperfections if hasattr(args, "imperfections") else 0.3

    rewriter = HumanRewriter(
        imperfection_level=imperfection,
    )
    constraints = RewriteConstraints(target_style=style)
    result = rewriter.rewrite(text, constraints=constraints)

    output = {
        "rewritten": result.rewritten,
        "ai_probability_before": result.ai_probability_before,
        "ai_probability_after": result.ai_probability_after,
        "human_score": result.human_score.overall,
        "meaning_preserved": result.meaning_preserved,
    }

    if args.output:
        Path(args.output).write_text(json.dumps(output, indent=2))
    else:
        print(result.rewritten)
    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    style = args.style or "conversational"

    rewriter = HumanRewriter(imperfection_level=0.3)
    constraints = RewriteConstraints(target_style=style)

    results = []
    for input_file in sorted(input_dir.glob("*.txt")):
        text = input_file.read_text()
        result = rewriter.rewrite(text, constraints=constraints)
        output_file = output_dir / input_file.name
        output_file.write_text(result.rewritten)
        results.append({
            "file": input_file.name,
            "human_score": result.human_score.overall,
            "ai_before": result.ai_probability_before,
            "ai_after": result.ai_probability_after,
        })

    print(json.dumps(results, indent=2))
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    original = _read_input(args.original)
    rewritten = _read_input(args.rewritten)

    original_ai = detect_ai_text(original)
    rewritten_ai = detect_ai_text(rewritten)
    rewritten_score = score_human_likeness(rewritten)

    result = {
        "original_ai_probability": original_ai["ai_probability"],
        "rewritten_ai_probability": rewritten_ai["ai_probability"],
        "human_likeness_score": rewritten_score["overall"],
        "improvement": original_ai["ai_probability"] - rewritten_ai["ai_probability"],
    }

    if args.blind_test:
        result["blind_test"] = "Human judges would need to distinguish original from rewritten"

    print(json.dumps(result, indent=2))
    return 0


def cmd_calibrate(args: argparse.Namespace) -> int:
    human_samples_dir = Path(args.human_samples)
    ai_samples_dir = Path(args.ai_samples)

    human_texts = []
    for f in human_samples_dir.glob("*.txt"):
        human_texts.append(f.read_text())

    ai_texts = []
    for f in ai_samples_dir.glob("*.txt"):
        ai_texts.append(f.read_text())

    human_scores = [score_human_likeness(t)["overall"] for t in human_texts]
    ai_scores = [detect_ai_text(t)["ai_probability"] for t in ai_texts]

    result = {
        "human_samples": len(human_texts),
        "ai_samples": len(ai_texts),
        "avg_human_score": sum(human_scores) / max(1, len(human_scores)),
        "avg_ai_probability": sum(ai_scores) / max(1, len(ai_scores)),
    }

    print(json.dumps(result, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="human-writer",
        description="Simulate human author writing style with AI detection and rewrite capabilities",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    detect_p = subparsers.add_parser("detect", help="Detect AI-generated text")
    detect_p.add_argument("text", help="Text to analyze or file path")
    detect_p.add_argument("--detailed", action="store_true", help="Show detailed feature scores")

    analyze_p = subparsers.add_parser("analyze", help="Analyze text human-likeness")
    analyze_p.add_argument("text", help="Text to analyze or file path")
    analyze_p.add_argument("--style-profile", default="conversational", choices=["conversational", "technical", "executive", "creative", "academic"])

    rewrite_p = subparsers.add_parser("rewrite", help="Rewrite text with human-like style")
    rewrite_p.add_argument("text", help="Text to rewrite or file path")
    rewrite_p.add_argument("--style", default="conversational", choices=["conversational", "technical", "executive", "creative", "academic"])
    rewrite_p.add_argument("--imperfections", type=float, default=0.3, help="Imperfection level (0-1)")
    rewrite_p.add_argument("--output", default="", help="Output file path")

    batch_p = subparsers.add_parser("batch", help="Batch rewrite files in a directory")
    batch_p.add_argument("--input-dir", required=True, help="Input directory")
    batch_p.add_argument("--output-dir", required=True, help="Output directory")
    batch_p.add_argument("--style", default="conversational", choices=["conversational", "technical", "executive", "creative", "academic"])

    compare_p = subparsers.add_parser("compare", help="Compare original and rewritten text")
    compare_p.add_argument("--original", required=True, help="Original text or file")
    compare_p.add_argument("--rewritten", required=True, help="Rewritten text or file")
    compare_p.add_argument("--blind-test", action="store_true", help="Include blind test info")

    calibrate_p = subparsers.add_parser("calibrate", help="Calibrate detector with sample corpora")
    calibrate_p.add_argument("--human-samples", required=True, help="Directory of human-written samples")
    calibrate_p.add_argument("--ai-samples", required=True, help="Directory of AI-generated samples")

    args = parser.parse_args()
    handlers = {
        "detect": cmd_detect,
        "analyze": cmd_analyze,
        "rewrite": cmd_rewrite,
        "batch": cmd_batch,
        "compare": cmd_compare,
        "calibrate": cmd_calibrate,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
