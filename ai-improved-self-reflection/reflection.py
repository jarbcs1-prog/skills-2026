"""
AI Self-Reflection Engine v2

Reflection processing layer.

Converts task experiences into structured
ReflectionEvent objects.

Pipeline position:

Task Experience
        ↓
Reflection Event
        ↓
Distillation
        ↓
Capability

This module only captures experience.
"""

from datetime import datetime
from typing import List

from models import (
    CommunicationAudit,
    FrictionType,
    ReflectionEvent,
)

from storage import (
    REFLECTION_MEMORY,
    append_json_record,
    append_markdown,
)


def normalize_confidence(
    confidence: float,
) -> float:
    """
    Ensure confidence remains within valid range.
    """

    return max(
        0.0,
        min(
            1.0,
            float(confidence),
        ),
    )


def normalize_evidence(
    evidence: int,
) -> int:
    """
    Prevent invalid evidence values.
    """

    return max(
        0,
        int(evidence),
    )


def classify_friction(
    category: str,
) -> FrictionType:
    """
    Convert human categories into friction types.

    Allows flexible user input while maintaining
    structured categories internally.
    """

    category = (
        category
        .lower()
        .strip()
    )

    mapping = {
        "structural": FrictionType.STRUCTURAL,
        "structure mismatch": FrictionType.STRUCTURAL,

        "epistemic": FrictionType.EPISTEMIC,

        "interaction": FrictionType.INTERACTION,

        "strategy": FrictionType.STRATEGY,
        "strategy friction": FrictionType.STRATEGY,
    }

    return mapping.get(
        category,
        FrictionType.UNKNOWN,
    )


def calculate_severity(
    communication: CommunicationAudit,
) -> float:
    """
    Estimate communication friction severity.

    0.0 = no friction
    1.0 = severe mismatch
    """

    return min(
        1.0,
        (
            communication.corrections * 0.20
            + communication.clarifications * 0.10
            + communication.re_prompts * 0.05
        ),
    )


def create_reflection(
    *,
    task: str,
    category: str,
    observation: str,
    friction: str,
    root_cause: str,
    lesson: str,
    scope: str,
    confidence: float,
    evidence: int,
    action: str,
    audience_assumptions: List[str] | None = None,
    hidden_criteria: List[str] | None = None,
    corrections: int = 0,
    clarifications: int = 0,
    re_prompts: int = 0,
) -> ReflectionEvent:
    """
    Create and persist a reflection event.
    """

    communication = CommunicationAudit(
        audience_assumptions=(
            audience_assumptions or []
        ),
        hidden_criteria=(
            hidden_criteria or []
        ),
        corrections=max(
            0,
            corrections,
        ),
        clarifications=max(
            0,
            clarifications,
        ),
        re_prompts=max(
            0,
            re_prompts,
        ),
    )

    event = ReflectionEvent(
        task=task,
        category=category,
        friction=friction,
        friction_type=classify_friction(
            category
        ),
        observation=observation,
        root_cause=root_cause,
        lesson=lesson,
        scope=scope,
        confidence=normalize_confidence(
            confidence
        ),
        evidence_count=normalize_evidence(
            evidence
        ),
        action=action,
        communication=communication,
        created=datetime.now().isoformat(),
    )

    append_json_record(
        REFLECTION_MEMORY,
        event,
    )

    append_markdown(
        format_markdown_entry(
            event
        )
    )

    return event


def format_markdown_entry(
    event: ReflectionEvent,
) -> str:
    """
    Create human-readable friction log entry.
    """

    return f"""
## {event.created} — {event.task}

**Category:** {event.category}

**Friction Type:** {event.friction_type.value}

**Observation:**
{event.observation}

**Friction:**
{event.friction}

**Root Cause:**
{event.root_cause}

**Generalized Lesson:**
{event.lesson}

**Scope:**
{event.scope}

**Confidence:**
{event.confidence}

**Evidence Count:**
{event.evidence_count}

**Communication Score:**
{event.communication.communication_score():.2f}

**Communication Severity:**
{calculate_severity(event.communication):.2f}

**Audience Assumptions:**
{", ".join(event.communication.audience_assumptions) or "None"}

**Hidden Criteria:**
{", ".join(event.communication.hidden_criteria) or "None"}

**Corrections:**
{event.communication.corrections}

**Clarifications:**
{event.communication.clarifications}

**Re-prompts:**
{event.communication.re_prompts}

**Future Action:**
{event.action}

---

"""


def load_reflections() -> list:
    """
    Convenience helper for later modules.
    """

    from storage import load_json

    return load_json(
        REFLECTION_MEMORY,
        [],
    )
