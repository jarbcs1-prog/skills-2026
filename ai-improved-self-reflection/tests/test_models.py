"""
Tests for models module.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    CommunicationAudit,
    FrictionType,
    PromotionLevel,
    ReflectionEvent,
    ReflectionCandidate,
    Capability,
    ValidationRecord,
    UnseenObservation,
    ObservationStatus,
    SCHEMA_VERSION,
)


def test_friction_type_enum():
    assert FrictionType.STRUCTURAL.value == "structural"
    assert FrictionType.EPISTEMIC.value == "epistemic"
    assert FrictionType.INTERACTION.value == "interaction"
    assert FrictionType.STRATEGY.value == "strategy"
    assert FrictionType.UNKNOWN.value == "unknown"
    print("PASS: FrictionType enum")


def test_promotion_level_enum():
    assert PromotionLevel.OBSERVATION.value == "observation"
    assert PromotionLevel.CANDIDATE.value == "candidate"
    assert PromotionLevel.LOCAL.value == "local"
    assert PromotionLevel.GLOBAL.value == "global"
    print("PASS: PromotionLevel enum")


def test_communication_audit_score():
    audit = CommunicationAudit()
    assert audit.communication_score() == 1.0

    audit.corrections = 1
    assert audit.communication_score() == 0.9

    audit.corrections = 3
    assert audit.communication_score() == 0.7

    audit.clarifications = 2
    assert audit.communication_score() == 0.6

    audit.re_prompts = 5
    score = audit.communication_score()
    assert score >= 0.0
    print("PASS: CommunicationAudit score")


def test_reflection_event_creation():
    event = ReflectionEvent(
        task="test task",
        category="structural",
        friction="test friction",
        friction_type=FrictionType.STRUCTURAL,
        observation="test observation",
        root_cause="test cause",
        lesson="test lesson",
        scope="test scope",
        confidence=0.85,
        evidence_count=3,
        action="test action",
    )
    assert event.task == "test task"
    assert event.confidence == 0.85
    assert event.schema_version == SCHEMA_VERSION
    print("PASS: ReflectionEvent creation")


def test_reflection_candidate_creation():
    candidate = ReflectionCandidate(
        lesson="test lesson",
        scope="test scope",
        source_events=3,
        confidence=0.8,
        transferability=0.75,
    )
    assert candidate.lesson == "test lesson"
    assert candidate.status == ObservationStatus.MONITORING
    assert candidate.validation_required is True
    print("PASS: ReflectionCandidate creation")


def test_capability_creation():
    cap = Capability(
        name="test capability",
        principle="test principle",
        scope=["scope1", "scope2"],
        evidence_count=5,
        confidence=0.9,
        validation_score=0.8,
        promotion_level=PromotionLevel.GLOBAL,
    )
    assert cap.name == "test capability"
    assert cap.active is True
    assert cap.promotion_level == PromotionLevel.GLOBAL
    print("PASS: Capability creation")


def test_validation_record_creation():
    record = ValidationRecord(
        capability_name="test cap",
        task="test task",
        outcome="test outcome",
        improvement_observed=True,
        confidence_delta=0.1,
    )
    assert record.capability_name == "test cap"
    assert record.improvement_observed is True
    print("PASS: ValidationRecord creation")


def test_unseen_observation_creation():
    obs = UnseenObservation(
        observation="test observation",
        possible_category="structural",
    )
    assert obs.status == ObservationStatus.MONITORING
    assert obs.evidence_count == 1
    print("PASS: UnseenObservation creation")


if __name__ == "__main__":
    test_friction_type_enum()
    test_promotion_level_enum()
    test_communication_audit_score()
    test_reflection_event_creation()
    test_reflection_candidate_creation()
    test_capability_creation()
    test_validation_record_creation()
    test_unseen_observation_creation()
    print("\nAll model tests passed!")
