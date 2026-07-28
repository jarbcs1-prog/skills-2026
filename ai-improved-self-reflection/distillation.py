"""
AI Self-Reflection Engine v2

Distillation layer.

Transforms reflection events into
candidate lessons.

Pipeline:

Reflection Events
        ↓
Pattern Detection
        ↓
Generalized Principle
        ↓
Reflection Candidate

This module does not activate capabilities.
"""

from collections import defaultdict
from typing import Dict, List

from models import (
    ObservationStatus,
    ReflectionCandidate,
)

from storage import (
    CANDIDATE_MEMORY,
    load_json,
    save_json,
)


MINIMUM_PATTERN_EVIDENCE = 2


def group_by_lesson(
    events: List[dict],
) -> Dict[str, List[dict]]:
    """
    Group reflection events by generalized lesson.

    Similar lessons become candidates for
    capability evaluation.
    """

    grouped = defaultdict(list)

    for event in events:
        lesson = event.get(
            "lesson",
            "",
        ).strip()

        if lesson:
            grouped[lesson].append(
                event
            )

    return grouped


def calculate_transferability(
    events: List[dict],
) -> float:
    """
    Estimate whether a lesson applies beyond
    the original situation.

    A lesson appearing across multiple scopes
    receives a higher score.
    """

    scopes = {
        event.get(
            "scope",
            "",
        )
        for event in events
    }

    scope_count = len(
        scopes
    )

    if scope_count >= 3:
        return 1.0

    if scope_count == 2:
        return 0.75

    return 0.50


def calculate_candidate_confidence(
    events: List[dict],
) -> float:
    """
    Aggregate confidence from supporting events.
    """

    if not events:
        return 0.0

    confidence_values = [
        float(
            event.get(
                "confidence",
                0.0,
            )
        )
        for event in events
    ]

    return round(
        sum(confidence_values)
        / len(confidence_values),
        2,
    )


def create_candidate(
    lesson: str,
    events: List[dict],
) -> ReflectionCandidate:
    """
    Convert repeated reflection events into
    a candidate lesson.
    """

    scope_values = {
        event.get(
            "scope",
            "",
        )
        for event in events
    }

    return ReflectionCandidate(
        lesson=lesson,
        scope=", ".join(
            sorted(
                scope_values
            )
        ),
        source_events=len(events),
        confidence=calculate_candidate_confidence(
            events
        ),
        transferability=calculate_transferability(
            events
        ),
        validation_required=True,
        status=ObservationStatus.MONITORING,
    )


def distill_candidates(
    reflections: List[dict],
) -> List[ReflectionCandidate]:
    """
    Extract candidate lessons from experiences.
    """

    grouped = group_by_lesson(
        reflections
    )

    candidates = []

    for lesson, events in grouped.items():

        if len(events) < MINIMUM_PATTERN_EVIDENCE:
            continue

        candidate = create_candidate(
            lesson,
            events,
        )

        candidates.append(
            candidate
        )

    return candidates


def save_candidates(
    candidates: List[ReflectionCandidate],
) -> None:
    """
    Persist candidate lessons.
    """

    existing = load_json(
        CANDIDATE_MEMORY,
        [],
    )

    existing_lessons = {
        item.get(
            "lesson"
        )
        for item in existing
    }

    for candidate in candidates:

        if candidate.lesson in existing_lessons:
            continue

        existing.append(
            {
                "lesson": candidate.lesson,
                "scope": candidate.scope,
                "source_events": candidate.source_events,
                "confidence": candidate.confidence,
                "transferability": candidate.transferability,
                "validation_required": (
                    candidate.validation_required
                ),
                "status": (
                    candidate.status.value
                ),
                "created": candidate.created,
                "schema_version": (
                    candidate.schema_version
                ),
            }
        )

    save_json(
        CANDIDATE_MEMORY,
        existing,
    )


def load_reflections_for_distillation() -> list:
    """
    Load reflections directly from storage.

    Avoids circular import with reflection module.
    """

    from storage import REFLECTION_MEMORY

    return load_json(
        REFLECTION_MEMORY,
        [],
    )


def run_distillation() -> List[ReflectionCandidate]:
    """
    Main distillation entry point.
    """

    reflections = load_reflections_for_distillation()

    candidates = distill_candidates(
        reflections
    )

    save_candidates(
        candidates
    )

    return candidates
