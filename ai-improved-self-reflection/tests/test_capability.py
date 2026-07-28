"""
Tests for capability module.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from capability import (
    calculate_promotion_score,
    determine_level,
    merge_capability,
)
from models import PromotionLevel


def test_calculate_promotion_score():
    score = calculate_promotion_score(
        evidence_count=5,
        confidence=0.8,
        transferability=0.75,
        validation_score=0.6,
    )
    assert 0.0 <= score <= 1.0
    assert score > 0
    print("PASS: calculate_promotion_score")


def test_calculate_promotion_score_zero_evidence():
    score = calculate_promotion_score(
        evidence_count=0,
        confidence=0.8,
        transferability=0.75,
        validation_score=0.6,
    )
    assert score == 0.0
    print("PASS: calculate_promotion_score zero")


def test_determine_level_global():
    level = determine_level(
        evidence_count=5,
        promotion_score=0.75,
    )
    assert level == PromotionLevel.GLOBAL
    print("PASS: determine_level global")


def test_determine_level_local():
    level = determine_level(
        evidence_count=3,
        promotion_score=0.55,
    )
    assert level == PromotionLevel.LOCAL
    print("PASS: determine_level local")


def test_determine_level_candidate():
    level = determine_level(
        evidence_count=2,
        promotion_score=0.5,
    )
    assert level == PromotionLevel.CANDIDATE
    print("PASS: determine_level candidate")


def test_merge_capability_new():
    existing = []
    from models import Capability
    
    cap = Capability(
        name="new capability",
        principle="new principle",
        scope=["scope1"],
        evidence_count=3,
        confidence=0.8,
        validation_score=0.6,
        promotion_level=PromotionLevel.LOCAL,
    )
    
    result = merge_capability(existing, cap)
    assert len(result) == 1
    assert result[0]["name"] == "new capability"
    print("PASS: merge_capability new")


def test_merge_capability_existing():
    existing = [
        {
            "name": "existing capability",
            "evidence_count": 3,
            "confidence": 0.8,
            "validation_score": 0.6,
        }
    ]
    
    from models import Capability
    
    cap = Capability(
        name="existing capability",
        principle="existing principle",
        scope=["scope1"],
        evidence_count=2,
        confidence=0.7,
        validation_score=0.5,
        promotion_level=PromotionLevel.CANDIDATE,
    )
    
    result = merge_capability(existing, cap)
    assert len(result) == 1
    assert result[0]["evidence_count"] == 5
    assert result[0]["confidence"] == 0.75
    print("PASS: merge_capability existing")


if __name__ == "__main__":
    test_calculate_promotion_score()
    test_calculate_promotion_score_zero_evidence()
    test_determine_level_global()
    test_determine_level_local()
    test_determine_level_candidate()
    test_merge_capability_new()
    test_merge_capability_existing()
    print("\nAll capability tests passed!")
