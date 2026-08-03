"""CLI for rap-writer skill."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.rhythm import analyze as analyze_rhythm
from scripts.rhyme import analyze as analyze_rhyme
from scripts.generator import adapt, generate, AdaptationConstraints
from scripts.styles import STYLE_PROFILES


def _read_input(input_arg: str) -> str:
    path = Path(input_arg)
    if path.exists():
        return path.read_text()
    return input_arg


def cmd_analyze(args: argparse.Namespace) -> int:
    lyrics = _read_input(args.lyrics)
    rhythm = analyze_rhythm(lyrics)
    rhyme = analyze_rhyme(lyrics)

    result = {
        "rhythm": {
            "overall_meter": rhythm.overall_meter,
            "tempo_hint": rhythm.tempo_hint,
            "total_lines": len(rhythm.lines),
            "avg_syllables": sum(l.syllable_count for l in rhythm.lines) / max(1, len(rhythm.lines)),
        },
        "rhyme": {
            "scheme": rhyme.rhyme_scheme,
            "end_rhyme_count": len(rhyme.end_rhymes),
            "internal_rhyme_count": len(rhyme.internal_rhymes),
            "density": rhyme.density,
            "multisyllabic_count": len(rhyme.multisyllabic),
        },
    }

    output = args.output
    if output:
        Path(output).write_text(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))
    return 0


def cmd_adapt(args: argparse.Namespace) -> int:
    original = _read_input(args.original)
    constraints = AdaptationConstraints(
        target_word_count=len(original.split()),
        style=args.style,
    )
    result = adapt(original, args.theme, constraints)

    output = args.output
    if output:
        Path(output).write_text(json.dumps({
            "adapted": result.adapted,
            "word_count_match": result.word_count_match,
            "rhyme_score": result.rhyme_score,
            "rhythm_score": result.rhythm_score,
        }, indent=2))
    else:
        print(json.dumps({
            "adapted": result.adapted,
            "word_count_match": result.word_count_match,
            "rhyme_score": result.rhyme_score,
            "rhythm_score": result.rhythm_score,
        }, indent=2))
    return 0


def cmd_write(args: argparse.Namespace) -> int:
    structure = args.structure.split("-")
    result = generate(args.theme, structure, args.style)

    output = args.output if hasattr(args, "output") else ""
    if output:
        Path(output).write_text(result.lyrics)
    else:
        print(result.lyrics)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    original = _read_input(args.original)
    adapted = _read_input(args.adapted)

    orig_word_count = len(original.split())
    adapt_word_count = len(adapted.split())

    result = {
        "original_word_count": orig_word_count,
        "adapted_word_count": adapt_word_count,
        "word_count_match": orig_word_count == adapt_word_count,
        "strict": args.strict,
    }

    if args.strict:
        result["pass"] = result["word_count_match"]
    else:
        result["pass"] = abs(orig_word_count - adapt_word_count) <= 2

    print(json.dumps(result, indent=2))
    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    styles = args.styles.split(",")
    results = []
    for style in styles:
        for i in range(args.count):
            structure = ["verse", "chorus", "verse", "chorus"]
            result = generate(args.theme, structure, style.strip())
            results.append({
                "style": style.strip(),
                "index": i + 1,
                "lyrics": result.lyrics,
            })

    print(json.dumps(results, indent=2))
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    lyrics = _read_input(args.lyrics)

    if args.format == "lrc":
        lines = lyrics.split("\n")
        lrc_lines = []
        for i, line in enumerate(lines):
            timestamp = f"{i * 4:02d}:{(i * 4 % 60):02d}.00"
            lrc_lines.append(f"[{timestamp}] {line}")
        content = "\n".join(lrc_lines)
    elif args.format == "json":
        content = json.dumps({"lyrics": lyrics, "bpm": args.bpm}, indent=2)
    else:
        content = lyrics

    print(content)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="rap-writer",
        description="Rap lyrics analysis, generation, adaptation, and validation",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_p = subparsers.add_parser("analyze", help="Analyze lyrics rhythm and rhyme")
    analyze_p.add_argument("--lyrics", required=True, help="Lyrics text or file path")
    analyze_p.add_argument("--output", default="", help="Output JSON file path")

    adapt_p = subparsers.add_parser("adapt", help="Adapt lyrics to a new theme")
    adapt_p.add_argument("--original", required=True, help="Original lyrics text or file")
    adapt_p.add_argument("--theme", required=True, help="New theme")
    adapt_p.add_argument("--style", default="boom-bap", choices=["boom-bap", "trap", "conscious", "drill", "lo-fi"])
    adapt_p.add_argument("--output", default="", help="Output file path")

    write_p = subparsers.add_parser("write", help="Generate original lyrics")
    write_p.add_argument("--theme", required=True, help="Theme for the lyrics")
    write_p.add_argument("--structure", default="verse-chorus", help="Song structure")
    write_p.add_argument("--style", default="boom-bap", choices=["boom-bap", "trap", "conscious", "drill", "lo-fi"])
    write_p.add_argument("--bars", type=int, default=16, help="Number of bars")

    validate_p = subparsers.add_parser("validate", help="Validate adaptation quality")
    validate_p.add_argument("--original", required=True, help="Original lyrics")
    validate_p.add_argument("--adapted", required=True, help="Adapted lyrics")
    validate_p.add_argument("--strict", action="store_true", help="Strict validation")

    batch_p = subparsers.add_parser("batch", help="Batch generate lyrics")
    batch_p.add_argument("--theme", required=True, help="Theme for the lyrics")
    batch_p.add_argument("--styles", required=True, help="Comma-separated styles")
    batch_p.add_argument("--count", type=int, default=3, help="Number of lyrics to generate")

    export_p = subparsers.add_parser("export", help="Export lyrics in different formats")
    export_p.add_argument("--lyrics", required=True, help="Lyrics text or file")
    export_p.add_argument("--format", default="text", choices=["text", "lrc", "json"])
    export_p.add_argument("--bpm", type=int, default=90, help="BPM for LRC export")

    args = parser.parse_args()
    handlers = {
        "analyze": cmd_analyze,
        "adapt": cmd_adapt,
        "write": cmd_write,
        "validate": cmd_validate,
        "batch": cmd_batch,
        "export": cmd_export,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
