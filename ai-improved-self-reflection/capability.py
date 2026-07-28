"""
AI Self-Reflection Engine v2

Capability promotion layer.

Transforms validated reflection candidates
into persistent behavioral capabilities.

Pipeline:

Candidate Lesson
        ↓
Evaluation
        ↓
Capability
        ↓
Behavioral Update

Promotion requires:

- evidence
- confidence
- transferability
- validation
"""

from typing import List

from models import (
    Capability,
    PromotionLevel,
)

from storage import (
    CAPABILITY_MEMORY,
    load_json,
    save_json,
)


MINIMUM_GLOBAL_EVIDENCE = 5

MINIMUM_LOCAL_EVIDENCE = 3


def calculate_promotion_score(
    *,
    evidence_count: int,
    confidence: float,
    transferability: float,
    validation_score: float,
) -> float:
    """
    Calculate capability readiness.

    The weighting intentionally prevents
    frequent but poorly validated patterns
    from becoming global behavior.
    """

    evidence_factor = min(
        1.0,
        evidence_count / 10,
    )

    score = (
        evidence_factor
        * confidence
        * transferability
        * validation_score
    )

    return round(
        score,
        3,
    )


def determine_level(
    *,
    evidence_count: int,
    promotion_score: float,
) -> PromotionLevel:
    """
    Determine capability maturity.
    """

    if (
        evidence_count >= MINIMUM_GLOBAL_EVIDENCE
        and promotion_score >= 0.75
    ):
        return PromotionLevel.GLOBAL

    if (
        evidence_count >= MINIMUM_LOCAL_EVIDENCE
        and promotion_score >= 0.55
    ):
        return PromotionLevel.LOCAL

    return PromotionLevel.CANDIDATE


def create_capability(
    candidate: dict,
    validation_score: float = 0.5,
) -> Capability:
    """
    Convert a candidate lesson into a capability.

    Validation defaults to neutral because a
    candidate may exist before testing.
    """

    evidence = candidate.get(
        "source_events",
        0,
    )

    confidence = candidate.get(
        "confidence",
        0.0,
    )

    transferability = candidate.get(
        "transferability",
        0.0,
    )

    promotion_score = calculate_promotion_score(
        evidence_count=evidence,
        confidence=confidence,
        transferability=transferability,
        validation_score=validation_score,
    )

    level = determine_level(
        evidence_count=evidence,
        promotion_score=promotion_score,
    )

    return Capability(
        name=candidate["lesson"],
        principle=candidate["lesson"],
        scope=[
            item.strip()
            for item in candidate.get(
                "scope",
                "",
            ).split(",")
            if item.strip()
        ],
        evidence_count=evidence,
        confidence=confidence,
        validation_score=validation_score,
        promotion_level=level,
    )


def merge_capability(
    existing: List[dict],
    capability: Capability,
) -> List[dict]:
    """
    Update existing capability instead of
    creating duplicates.
    """

    for item in existing:

        if item.get(
            "name"
        ) != capability.name:
            continue

        item["evidence_count"] = (
            item.get(
                "evidence_count",
                0,
            )
            + capability.evidence_count
        )

        item["confidence"] = round(
            (
                item.get(
                    "confidence",
                    0.0,
                )
                + capability.confidence
            )
            / 2,
            2,
        )

        item["validation_score"] = round(
            (
                item.get(
                    "validation_score",
                    0.5,
                )
                + capability.validation_score
            )
            / 2,
            2,
        )

        return existing

    existing.append(
        {
            "name": capability.name,
            "principle": capability.principle,
            "scope": capability.scope,
            "evidence_count": capability.evidence_count,
            "confidence": capability.confidence,
            "validation_score": capability.validation_score,
            "promotion_level": (
                capability.promotion_level.value
            ),
            "active": True,
            "created": capability.created,
            "schema_version": capability.schema_version,
        }
    )

    return existing


def promote_candidates() -> List[dict]:
    """
    Evaluate candidate lessons and update
    capability memory.
    """

    candidate_memory = load_json(
        CAPABILITY_MEMORY,
        {},
    )

    candidates = candidate_memory.get(
        "candidate_lessons",
        [],
    )

    capabilities = candidate_memory.get(
        "capabilities",
        [],
    )

    promoted = []

    for candidate in candidates:

        capability = create_capability(
            candidate
        )

        capabilities = merge_capability(
            capabilities,
            capability,
        )

        promoted.append(
            capability
        )

    candidate_memory["capabilities"] = (
        capabilities
    )

    save_json(
        CAPABILITY_MEMORY,
        candidate_memory,
    )

    return promoted


def deprecate_pattern(
    pattern: str,
    replacement: str,
) -> None:
    """
    Record a pattern that should be reduced.
    """

    memory = load_json(
        CAPABILITY_MEMORY,
        {},
    )

    deprecated = memory.get(
        "deprecated_patterns",
        [],
    )

    deprecated.append(
        {
            "pattern": pattern,
            "replacement": replacement,
        }
    )

    memory["deprecated_patterns"] = deprecated

    save_json(
        CAPABILITY_MEMORY,
        memory,
    )
