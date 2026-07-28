"""
AI Self-Reflection Engine v2

Validation layer.

Measures whether promoted capabilities
actually improve future outcomes.

A capability should not remain active
because it sounds correct.

It should remain active because it works.
"""

from datetime import datetime
from typing import List

from models import ValidationRecord

from storage import (
    CAPABILITY_MEMORY,
    VALIDATION_MEMORY,
    append_json_record,
    load_json,
    save_json,
)


def record_validation(
    *,
    capability_name: str,
    task: str,
    outcome: str,
    improvement_observed: bool,
    confidence_delta: float,
) -> ValidationRecord:
    """
    Record evidence that a capability helped
    or failed to help.
    """

    record = ValidationRecord(
        capability_name=capability_name,
        task=task,
        outcome=outcome,
        improvement_observed=improvement_observed,
        confidence_delta=max(
            -1.0,
            min(
                1.0,
                confidence_delta,
            ),
        ),
        created=datetime.now().isoformat(),
    )

    append_json_record(
        VALIDATION_MEMORY,
        record,
    )

    update_capability_validation(
        record
    )

    return record


def get_capability_validations(
    capability_name: str,
) -> List[dict]:
    """
    Retrieve validation history for
    a specific capability.
    """

    records = load_json(
        VALIDATION_MEMORY,
        [],
    )

    return [
        record
        for record in records
        if record.get(
            "capability_name"
        ) == capability_name
    ]


def calculate_validation_score(
    capability_name: str,
) -> float:
    """
    Calculate capability reliability.

    Positive improvements increase score.
    Failed applications reduce confidence.
    """

    records = get_capability_validations(
        capability_name
    )

    if not records:
        return 0.5

    score = 0.5

    for record in records:

        if record.get(
            "improvement_observed",
            False,
        ):
            score += 0.10

        else:
            score -= 0.10

    return round(
        max(
            0.0,
            min(
                1.0,
                score,
            ),
        ),
        2,
    )


def update_capability_validation(
    validation: ValidationRecord,
) -> None:
    """
    Update capability confidence after
    validation evidence arrives.
    """

    memory = load_json(
        CAPABILITY_MEMORY,
        {},
    )

    capabilities = memory.get(
        "capabilities",
        [],
    )

    for capability in capabilities:

        if capability.get(
            "name"
        ) != validation.capability_name:
            continue

        current_confidence = capability.get(
            "confidence",
            0.0,
        )

        capability["confidence"] = round(
            max(
                0.0,
                min(
                    1.0,
                    current_confidence
                    + validation.confidence_delta,
                ),
            ),
            2,
        )

        capability["validation_score"] = (
            calculate_validation_score(
                validation.capability_name
            )
        )

        capability["last_validated"] = (
            validation.created
        )

    memory["capabilities"] = capabilities

    save_json(
        CAPABILITY_MEMORY,
        memory,
    )


def find_weak_capabilities(
    threshold: float = 0.40,
) -> List[dict]:
    """
    Find capabilities that may need review.

    A capability with poor validation may be:

    - too narrow,
    - incorrectly generalized,
    - or no longer useful.
    """

    memory = load_json(
        CAPABILITY_MEMORY,
        {},
    )

    capabilities = memory.get(
        "capabilities",
        [],
    )

    return [
        capability
        for capability in capabilities
        if capability.get(
            "validation_score",
            0.0,
        ) < threshold
    ]


def deactivate_capability(
    capability_name: str,
) -> None:
    """
    Disable a capability without deleting history.

    Preserves learning history while preventing
    harmful behavior persistence.
    """

    memory = load_json(
        CAPABILITY_MEMORY,
        {},
    )

    capabilities = memory.get(
        "capabilities",
        [],
    )

    for capability in capabilities:

        if capability.get(
            "name"
        ) == capability_name:
            capability["active"] = False

    memory["capabilities"] = capabilities

    save_json(
        CAPABILITY_MEMORY,
        memory,
    )
