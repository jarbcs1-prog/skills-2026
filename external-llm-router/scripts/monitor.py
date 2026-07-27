"""External LLM Router — Usage monitor.

Tracks cumulative token consumption in a JSON file, auto-resets on new days,
and exits with code 1 when the daily limit is exceeded.

Usage:
    python monitor.py --file usage.json --add 1500 --limit 100000
    python monitor.py --file usage.json --status --limit 100000
    python monitor.py --file usage.json --reset
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def _load_usage(path: Path) -> dict[str, Any]:
    """Load the usage JSON, returning a default structure on any error."""
    default: dict[str, Any] = {"total": 0, "date": ""}
    if not path.is_file():
        return default
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            return default
        data.setdefault("total", 0)
        data.setdefault("date", "")
        return data
    except (json.JSONDecodeError, OSError):
        return default


def _save_usage(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")


def _maybe_reset(data: dict[str, Any]) -> dict[str, Any]:
    """Reset counter if we've rolled into a new day."""
    today = date.today().isoformat()
    if data.get("date") != today:
        data["total"] = 0
        data["date"] = today
    return data


def track_usage(path: Path, tokens: int, limit: int) -> tuple[bool, int]:
    """Add *tokens* to the running total and check against *limit*.

    Returns ``(limit_reached, current_total)``.
    """
    data = _load_usage(path)
    data = _maybe_reset(data)
    data["total"] += tokens
    _save_usage(path, data)
    return data["total"] >= limit, data["total"]


def get_status(path: Path, limit: int) -> tuple[bool, int]:
    """Return current usage without modifying it."""
    data = _load_usage(path)
    data = _maybe_reset(data)
    return data["total"] >= limit, data["total"]


def reset_usage(path: Path) -> None:
    """Zero out the usage file for today."""
    today = date.today().isoformat()
    _save_usage(path, {"total": 0, "date": today})
    print(f"Usage reset to 0 for {today}.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Track daily LLM token usage against a limit.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--file", "-f",
        default="daily_usage.json",
        help="Path to the JSON usage file (default: daily_usage.json)",
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--add", "-a",
        type=int,
        metavar="N",
        help="Add N tokens to the running total",
    )
    group.add_argument(
        "--status", "-s",
        action="store_true",
        help="Show current usage without modifying it",
    )
    group.add_argument(
        "--reset", "-r",
        action="store_true",
        help="Reset the usage counter to zero",
    )
    p.add_argument(
        "--limit", "-l",
        type=int,
        default=100_000,
        help="Daily token limit (default: 100000)",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    args = _build_parser().parse_args(argv)
    path = Path(args.file)

    if args.reset:
        reset_usage(path)
        return

    if args.status:
        reached, total = get_status(path, args.limit)
        status = "REACHED" if reached else "OK"
        print(f"Status: {status} | Total: {total}/{args.limit}")
        sys.exit(1 if reached else 0)

    # --add mode
    reached, total = track_usage(path, args.add, args.limit)
    status = "REACHED" if reached else "OK"
    print(f"Status: {status} | Total: {total}/{args.limit}")
    sys.exit(1 if reached else 0)


if __name__ == "__main__":
    main()
