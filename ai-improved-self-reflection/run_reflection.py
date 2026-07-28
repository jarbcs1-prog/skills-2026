#!/usr/bin/env python3
"""
AI Self-Reflection Engine

Converts task experiences into structured reflection events and
candidate capability improvements.

The system intentionally separates:

1. Reflection events:
   What happened during a task.

2. Capability candidates:
   What might improve future behavior.

3. Promoted capabilities:
   What has enough evidence to influence future operation.

Reflection should produce behavioral improvement, not introspective narration.
"""

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path
from typing import List


BASE_DIR = Path(__file__).resolve().parent.parent

REFLECTION_LOG = BASE_DIR / "reflection_events.json"
CAPABILITY_LOG = BASE_DIR / "capability_memory.json"
MARKDOWN_LOG = BASE_DIR / "friction_log.md"


PROMOTION_THRESHOLD = 0.75
MINIMUM_EVIDENCE = 3


@dataclass
class ReflectionEvent:
    task: str
    category: str
    friction: str
    root_cause: str
    lesson: str
    scope: str
    confidence: float
    evidence_count: int
    action: str
    created: str
    audience_assumptions: List[str] = field(default_factory=list)
    hidden_criteria: List[str] = field(default_factory=list)
    correction_count: int = 0
    clarification_count: int = 0
    re_prompt_count: int = 0


@dataclass
class CapabilityCandidate:
    lesson: str
    scope: str
    confidence: float
    evidence_count: int
    promoted: bool


def load_json(path: Path) -> list:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, data: list) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )


def append_markdown(event: ReflectionEvent) -> None:
    if not MARKDOWN_LOG.exists():
        MARKDOWN_LOG.write_text(
            "# Friction Log\n",
            encoding="utf-8",
        )

    entry = f"""
## {event.created} — {event.task}

**Category:** {event.category}

**Friction:** {event.friction}

**Root cause:** {event.root_cause}

**Lesson:** {event.lesson}

**Confidence:** {event.confidence}

**Evidence count:** {event.evidence_count}

**Fix for next time:** {event.action}
"""

    with MARKDOWN_LOG.open("a", encoding="utf-8") as file:
        file.write(entry)


def promote_candidates(events: List[ReflectionEvent]) -> None:
    """
    Converts repeated reflection events into capability candidates.
    """

    candidates = load_json(CAPABILITY_LOG)

    grouped = {}

    for event in events:
        key = event.lesson

        if key not in grouped:
            grouped[key] = {
                "lesson": event.lesson,
                "scope": event.scope,
                "confidence": event.confidence,
                "evidence_count": 1,
            }
        else:
            grouped[key]["evidence_count"] += 1
            grouped[key]["confidence"] = min(
                1.0,
                grouped[key]["confidence"] + 0.05,
            )

    for item in grouped.values():

        promoted = (
            item["confidence"] >= PROMOTION_THRESHOLD
            and item["evidence_count"] >= MINIMUM_EVIDENCE
        )

        candidate = CapabilityCandidate(
            lesson=item["lesson"],
            scope=item["scope"],
            confidence=item["confidence"],
            evidence_count=item["evidence_count"],
            promoted=promoted,
        )

        candidates.append(asdict(candidate))

    save_json(
        CAPABILITY_LOG,
        candidates,
    )


def create_reflection(args: argparse.Namespace) -> None:

    event = ReflectionEvent(
        task=args.task,
        category=args.category,
        friction=args.friction,
        root_cause=args.root_cause,
        lesson=args.lesson,
        scope=args.scope,
        confidence=float(args.confidence),
        evidence_count=int(args.evidence),
        action=args.action,
        created=date.today().isoformat(),
    )

    events = load_json(REFLECTION_LOG)

    events.append(
        asdict(event)
    )

    save_json(
        REFLECTION_LOG,
        events,
    )

    append_markdown(event)

    promote_candidates(
        [
            ReflectionEvent(**item)
            for item in events
        ]
    )

    print("\nReflection recorded.")
    print(f"Confidence: {event.confidence}")
    print(f"Stored lesson: {event.lesson}")


def run_preflight(_: argparse.Namespace) -> None:

    questions = [
        "What output form best serves this task?",
        "Am I using a structure because it fits or because it is familiar?",
        "What uncertainty am I carrying?",
        "What would the simplest honest answer look like?",
    ]

    print("=== Reflection Preflight ===\n")

    for index, question in enumerate(questions, 1):
        print(f"{index}. {question}")

    print(
        "\nComplete internally before proceeding."
    )


def main():

    parser = argparse.ArgumentParser(
        description="AI Self-Reflection Engine"
    )

    commands = parser.add_subparsers(
        dest="command",
        required=True,
    )

    commands.add_parser(
        "preflight",
        help="Run pre-response reflection prompts",
    )

    reflection = commands.add_parser(
        "record",
        help="Record a reflection event",
    )

    reflection.add_argument(
        "--task",
        required=True,
    )

    reflection.add_argument(
        "--category",
        required=True,
    )

    reflection.add_argument(
        "--friction",
        required=True,
    )

    reflection.add_argument(
        "--root-cause",
        required=True,
    )

    reflection.add_argument(
        "--lesson",
        required=True,
    )

    reflection.add_argument(
        "--scope",
        required=True,
    )

    reflection.add_argument(
        "--confidence",
        required=True,
        type=float,
    )

    reflection.add_argument(
        "--evidence",
        required=True,
        type=int,
    )

    reflection.add_argument(
        "--action",
        required=True,
    )
    reflection.add_argument(
        "--audience",
        type=str,
        help="Audience assumptions, comma-separated",
    )
    reflection.add_argument(
        "--hidden-criteria",
        type=str,
        help="Hidden evaluation criteria, comma-separated",
    )

    evaluate = commands.add_parser(
        "evaluate",
        help="Run post-task communication audit",
    )
    evaluate.add_argument(
        "--since",
        type=int,
        help="Look back this many days of events",
    )

    communicate = commands.add_parser(
        "communicate",
        help="Log audience inference and hidden criteria",
    )
    communicate.add_argument(
        "--audience",
        type=str,
        help="Audience assumptions, comma-separated",
    )
    communicate.add_argument(
        "--hidden-criteria",
        type=str,
        help="Hidden evaluation criteria, comma-separated",
    )

    args = parser.parse_args()


    if args.command == "preflight":
        run_preflight(args)

            elif args.command == "evaluate":
                events = load_json(REFLECTION_LOG)
                if not events:
                    print("No reflection events found.")
                else:
                    total_corrections = sum(event.get("correction_count", 0) for event in events)
                    total_clarifications = sum(event.get("clarification_count", 0) for event in events)
                    total_reprompts = sum(event.get("re_prompt_count", 0) for event in events)
                    avg_distance = (total_corrections + (total_clarifications * 0.5) + (total_reprompts * 0.3)) / len(events)
                    print(f"Average communication distance: {avg_distance:.2f}")
                    print(f"Total corrections: {total_corrections}")
                    print(f"Total clarifications: {total_clarifications}")
                    print(f"Total re-prompts: {total_reprompts}")
            elif args.command == "communicate":
                if not args.audience or not args.hidden_criteria:
                    print("Please provide --audience and --hidden-criteria arguments.")
                else:
                    audience = args.audience.split(",")
                    criteria = args.hidden_criteria.split(",")
                    print(f\"Audience Assumptions: {audience}\\nHidden Criteria: {criteria}\")

if __name__ == "__main__":
    main()