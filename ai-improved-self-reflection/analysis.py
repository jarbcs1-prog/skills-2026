"""
AI Self-Reflection Engine v2

Analysis layer.

Provides visibility into:

- reflection trends
- friction frequency
- capability health
- validation status

This module is read-only.

It observes the learning system
without changing the learning system.
"""

from collections import Counter
from typing import Dict, List

from storage import (
    REFLECTION_MEMORY,
    CAPABILITY_MEMORY,
    VALIDATION_MEMORY,
    load_json,
)


def load_reflection_data() -> List[dict]:
    """
    Load reflection events.
    """

    return load_json(
        REFLECTION_MEMORY,
        [],
    )


def load_capability_data() -> dict:
    """
    Load capability memory.
    """

    return load_json(
        CAPABILITY_MEMORY,
        {
            "capabilities": [],
            "candidate_lessons": [],
            "deprecated_patterns": [],
        },
    )


def load_validation_data() -> List[dict]:
    """
    Load validation records.
    """

    return load_json(
        VALIDATION_MEMORY,
        [],
    )


def friction_distribution() -> Dict[str, int]:
    """
    Count friction categories.

    Helps identify recurring process failures.
    """

    reflections = load_reflection_data()

    categories = [
        event.get(
            "category",
            "unknown",
        )
        for event in reflections
    ]

    return dict(
        Counter(categories)
    )


def most_common_friction(
    limit: int = 5,
) -> List[tuple]:
    """
    Return highest-frequency friction patterns.
    """

    distribution = friction_distribution()

    return sorted(
        distribution.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:limit]


def reflection_statistics() -> dict:
    """
    Summarize reflection history.
    """

    reflections = load_reflection_data()

    if not reflections:
        return {
            "total_reflections": 0,
            "average_confidence": 0,
            "average_evidence": 0,
        }

    confidence = [
        float(
            event.get(
                "confidence",
                0,
            )
        )
        for event in reflections
    ]

    evidence = [
        int(
            event.get(
                "evidence_count",
                0,
            )
        )
        for event in reflections
    ]

    return {
        "total_reflections": len(
            reflections
        ),
        "average_confidence": round(
            sum(confidence)
            / len(confidence),
            2,
        ),
        "average_evidence": round(
            sum(evidence)
            / len(evidence),
            2,
        ),
    }


def capability_statistics() -> dict:
    """
    Summarize capability state.
    """

    memory = load_capability_data()

    capabilities = memory.get(
        "capabilities",
        [],
    )

    levels = Counter(
        capability.get(
            "promotion_level",
            "unknown",
        )
        for capability in capabilities
    )

    active = sum(
        1
        for capability in capabilities
        if capability.get(
            "active",
            False,
        )
    )

    return {
        "total_capabilities": len(
            capabilities
        ),
        "active_capabilities": active,
        "promotion_levels": dict(
            levels
        ),
    }


def validation_statistics() -> dict:
    """
    Summarize capability validation.
    """

    validations = load_validation_data()

    if not validations:
        return {
            "total_validations": 0,
            "successful_validations": 0,
            "success_rate": 0,
        }

    successes = sum(
        1
        for validation in validations
        if validation.get(
            "improvement_observed",
            False,
        )
    )

    return {
        "total_validations": len(
            validations
        ),
        "successful_validations": successes,
        "success_rate": round(
            successes
            / len(validations),
            2,
        ),
    }


def capability_health_report() -> List[dict]:
    """
    Identify capability risks.

    A capability may require review when:

    - validation is weak
    - confidence is low
    - evidence is insufficient
    """

    memory = load_capability_data()

    capabilities = memory.get(
        "capabilities",
        [],
    )

    report = []

    for capability in capabilities:

        confidence = capability.get(
            "confidence",
            0,
        )

        validation = capability.get(
            "validation_score",
            0,
        )

        evidence = capability.get(
            "evidence_count",
            0,
        )

        risk = (
            confidence < 0.5
            or validation < 0.5
            or evidence < 3
        )

        report.append(
            {
                "name": capability.get(
                    "name"
                ),
                "risk": risk,
                "confidence": confidence,
                "validation": validation,
                "evidence": evidence,
            }
        )

    return report


def generate_system_report() -> dict:
    """
    Generate complete reflection system overview.
    """

    return {
        "reflection": reflection_statistics(),
        "friction_patterns": (
            most_common_friction()
        ),
        "capabilities": capability_statistics(),
        "validation": validation_statistics(),
        "capability_health": (
            capability_health_report()
        ),
    }
