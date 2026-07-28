"""
Tests for reflection module.
"""

import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from reflection import (
    normalize_confidence,
    normalize_evidence,
    classify_friction,
    calculate_severity,
    create_reflection,
    format_markdown_entry,
)
from models import FrictionType, CommunicationAudit


def test_normalize_confidence():
    assert normalize_confidence(0.5) == 0.5
    assert normalize_confidence(1.5) == 1.0
    assert normalize_confidence(-0.5) == 0.0
    print("PASS: normalize_confidence")


def test_normalize_evidence():
    assert normalize_evidence(5) == 5
    assert normalize_evidence(-3) == 0
    assert normalize_evidence(0) == 0
    print("PASS: normalize_evidence")


def test_classify_friction():
    assert classify_friction("structural") == FrictionType.STRUCTURAL
    assert classify_friction("STRUCTURAL") == FrictionType.STRUCTURAL
    assert classify_friction("structure mismatch") == FrictionType.STRUCTURAL
    assert classify_friction("epistemic") == FrictionType.EPISTEMIC
    assert classify_friction("interaction") == FrictionType.INTERACTION
    assert classify_friction("strategy") == FrictionType.STRATEGY
    assert classify_friction("strategy friction") == FrictionType.STRATEGY
    assert classify_friction("unknown type") == FrictionType.UNKNOWN
    print("PASS: classify_friction")


def test_calculate_severity():
    audit = CommunicationAudit()
    assert calculate_severity(audit) == 0.0

    audit.corrections = 5
    assert calculate_severity(audit) == 1.0

    audit.corrections = 2
    audit.clarifications = 3
    severity = calculate_severity(audit)
    assert 0.0 <= severity <= 1.0
    print("PASS: calculate_severity")


def test_format_markdown_entry():
    from models import ReflectionEvent
    
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
    
    entry = format_markdown_entry(event)
    assert "test task" in entry
    assert "test lesson" in entry
    assert "structural" in entry
    print("PASS: format_markdown_entry")


if __name__ == "__main__":
    test_normalize_confidence()
    test_normalize_evidence()
    test_classify_friction()
    test_calculate_severity()
    test_format_markdown_entry()
    print("\nAll reflection tests passed!")
