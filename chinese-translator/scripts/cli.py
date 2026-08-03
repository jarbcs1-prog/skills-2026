"""
CLI interface for chinese-translator.

Subcommands:
  translate  -- translate text (with optional glossary/TM)
  batch      -- translate all text files in a directory
  validate   -- compute quality scores for a file
  glossary    -- create or check a glossary
  tm         -- manage a translation memory
"""
import argparse
import json
import sys
from pathlib import Path

from scripts.domains import DOMAINS
from scripts.glossary import Glossary, load_glossary, save_glossary
from scripts.quality import compute_quality_scores, overall
from scripts.translator import ChineseTranslator, create_domain_glossary, translate_file
from scripts.translation_memory import TranslationMemory, load_tm, save_tm

ERROR_EXTS = {".docx", ".xlsx", ".pptx"}


def _load_glossary(path):
    if path is None:
        return None
    p = Path(path)
    if not p.exists():
        print(f"ERROR: glossary file {p} not found", file=sys.stderr)
        sys.exit(1)
    return load_glossary(p)


def _load_tm(path):
    if path is None:
        return None
    p = Path(path)
    if not p.exists():
        print(f"ERROR: translation memory file {p} not found", file=sys.stderr)
        sys.exit(1)
    return load_tm(p)


def _glossary_path(args):
    return getattr(args, "glossary", None)


def _tm_path(args):
    return getattr(args, "tm", None)


def _do_translate(args):
    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
    elif args.text:
        text = " ".join(args.text)
    else:
        print("ERROR: provide text or --input", file=sys.stderr)
        sys.exit(2)
    gl = _load_glossary(_glossary_path(args))
    tm = _load_tm(_tm_path(args))
    translator = ChineseTranslator(glossary=gl, tm=tm)
    result = translator.translate(text, domain=args.domain, style=args.style)
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


def _do_batch(args):
    gl = _load_glossary(_glossary_path(args))
    tm = _load_tm(_tm_path(args))
    translator = ChineseTranslator(glossary=gl, tm=tm)
    in_dir = Path(args.input)
    out_dir = Path(args.output)
    if not in_dir.exists():
        print(f"ERROR: input directory {in_dir} not found", file=sys.stderr)
        sys.exit(1)
    out_dir.mkdir(parents=True, exist_ok=True)
    processed = 0
    errors = 0
    for path in sorted(in_dir.rglob("*")):
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        if ext in ERROR_EXTS:
            print(f"ERROR: {ext} support requires optional library", file=sys.stderr)
            errors += 1
            continue
        if ext not in {".txt", ".md", ".srt", ".po"}:
            errors += 1
            continue
        out_path = out_dir / path.relative_to(in_dir)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            translate_file(str(path), str(out_path), translator, args.domain)
            processed += 1
        except Exception as exc:
            print(f"ERROR translating {path}: {exc}", file=sys.stderr)
            errors += 1
    print(json.dumps({"processed": processed, "errors": errors, "output_dir": str(out_dir)}))
    return 0


def _do_validate(args):
    text = Path(args.input).read_text(encoding="utf-8")
    gl = _load_glossary(_glossary_path(args))
    translator = ChineseTranslator(glossary=gl)
    result = translator.validate(text, text, threshold=args.threshold)
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


def _do_glossary(args):
    if args.cmd == "create":
        glossary = create_domain_glossary(args.domain)
        if args.output:
            save_glossary(args.output, glossary)
            print(f"Glossary saved to {args.output} ({len(glossary)} terms)")
        else:
            print(json.dumps(glossary.to_dict(), indent=2, ensure_ascii=True))
        return 0
    # check
    gl = _load_glossary(_glossary_path(args))
    text = Path(args.text).read_text(encoding="utf-8") if args.text.endswith((".txt", ".md")) else args.text
    violations = gl.check(text)
    print(json.dumps({"violations": violations, "count": len(violations)}, indent=2, ensure_ascii=True))
    return 0


def _do_tm(args):
    if args.tm_cmd == "add":
        p = Path(args.tm)
        tm = load_tm(p) if p.exists() else TranslationMemory()
        tm.add(args.source, args.translation, args.domain)
        save_tm(p, tm)
        print(f"Added entry to {p} ({len(tm)} total)")
        return 0
    # lookup
    text = args.text
    if not text:
        print("ERROR: provide --text", file=sys.stderr)
        sys.exit(2)
    if args.tm.lower() == "__inline__":
        tm = TranslationMemory(args.entries or [])
    else:
        tm = _load_tm(args.tm)
    result = tm.lookup(text)
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="chinese-translator")
    sub = parser.add_subparsers(dest="action", required=True)

    t = sub.add_parser("translate", help="Translate text or a file")
    t.add_argument("text", nargs="*", help="Input text")
    t.add_argument("--input", help="Input file")
    t.add_argument("--domain", choices=["auto", "legal", "technical", "medical", "business", "literary", "marketing"], default="auto")
    t.add_argument("--style", default="neutral")
    t.add_argument("--glossary", help="Path to glossary JSON file")
    t.add_argument("--tm", help="Path to translation memory JSON file")
    t.set_defaults(func=_do_translate)

    b = sub.add_parser("batch", help="Batch translate a directory")
    b.add_argument("--input", required=True)
    b.add_argument("--output", required=True)
    b.add_argument("--glossary")
    b.add_argument("--tm")
    b.add_argument("--domain", default="auto")
    b.set_defaults(func=_do_batch)

    v = sub.add_parser("validate", help="Validate adequacy of a file")
    v.add_argument("--input", required=True)
    v.add_argument("--threshold", type=float, default=0.5)
    v.add_argument("--glossary")
    v.set_defaults(func=_do_validate)

    g = sub.add_parser("glossary", help="Manage glossaries")
    g.add_argument("cmd", choices=["create", "check"])
    g.add_argument("--domain")
    g.add_argument("--output")
    g.add_argument("--text", help="Glossary file or inline text for check")
    g.add_argument("--glossary", help="Path to glossary JSON file")
    g.set_defaults(func=_do_glossary)

    tm = sub.add_parser("tm", help="Manage translation memory")
    tm.add_argument("tm_cmd", choices=["add", "lookup"])
    tm.add_argument("--tm", help="TM JSON file path")
    tm.add_argument("--source")
    tm.add_argument("--translation")
    tm.add_argument("--text")
    tm.add_argument("--domain", default="general")
    tm.add_argument("--entries", nargs="*", help="Inline JSON entries for lookup")
    tm.set_defaults(func=_do_tm)

    return parser


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
