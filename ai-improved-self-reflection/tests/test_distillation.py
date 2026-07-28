"""
Tests for distillation module.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from distillation import (
    group_by_lesson,
    calculate_transferability,
    calculate_candidate_confidence,
    create_candidate,
    distill_candidates,
)


def test_group_by_lesson():
    events = [
        {"lesson": "lesson A", "scope": "scope1"},
        {"lesson": "lesson B", "scope": "scope2"},
        {"lesson": "lesson A", "scope": "scope3"},
    ]
    
    grouped = group_by_lesson(events)
    assert len(grouped) == 2
    assert len(grouped["lesson A"]) == 2
    assert len(grouped["lesson B"]) == 1
    print("PASS: group_by_lesson")


def test_calculate_transferability_single_scope():
    events = [{"scope": "scope1"}]
    assert calculate_transferability(events) == 0.50
    
    events = [{"scope": "scope1"}, {"scope": "scope1"}]
    assert calculate_transferability(events) == 0.50
    print("PASS: calculate_transferability single")


def test_calculate_transferability_two_scopes():
    events = [{"scope": "scope1"}, {"scope": "scope2"}]
    assert calculate_transferability(events) == 0.75
    print("PASS: calculate_transferability two")


def test_calculate_transferability_three_scopes():
    events = [{"scope": "scope1"}, {"scope": "scope2"}, {"scope": "scope3"}]
    assert calculate_transferability(events) == 1.0
    print("PASS: calculate_transferability three")


def test_calculate_candidate_confidence():
    events = [
        {"confidence": 0.8},
        {"confidence": 0.6},
    ]
    result = calculate_candidate_confidence(events)
    assert result == 0.7
    print("PASS: calculate_candidate_confidence")


def test_calculate_candidate_confidence_empty():
    assert calculate_candidate_confidence([]) == 0.0
    print("PASS: calculate_candidate_confidence empty")


def test_create_candidate():
    events = [
        {"lesson": "test", "scope": "scope1", "confidence": 0.8},
        {"lesson": "test", "scope": "scope2", "confidence": 0.6},
    ]
    
    candidate = create_candidate("test", events)
    assert candidate.lesson == "test"
    assert candidate.source_events == 2
    assert candidate.confidence == 0.7
    assert candidate.transferability == 0.75
    print("PASS: create_candidate")


def test_distill_candidates_minimum_evidence():
    events = [
        {"lesson": "single", "scope": "scope1", "confidence": 0.8},
    ]
    
    candidates = distill_candidates(events)
    assert len(candidates) == 0
    print("PASS: distill_candidates minimum")


def test_distill_candidates_multiple():
    events = [
        {"lesson": "lesson A", "scope": "scope1", "confidence": 0.8},
        {"lesson": "lesson A", "scope": "scope2", "confidence": 0.6},
        {"lesson": "lesson B", "scope": "scope1", "confidence": 0.9},
        {"lesson": "lesson B", "scope": "scope1", "confidence": 0.7},
        {"lesson": "lesson B", "scope": "scope1", "confidence": 0.8},
    ]
    
    candidates = distill_candidates(events)
    assert len(candidates) == 2
    print("PASS: distill_candidates multiple")


if __name__ == "__main__":
    test_group_by_lesson()
    test_calculate_transferability_single_scope()
    test_calculate_transferability_two_scopes()
    test_calculate_transferability_three_scopes()
    test_calculate_candidate_confidence()
    test_calculate_candidate_confidence_empty()
    test_create_candidate()
    test_distill_candidates_minimum_evidence()
    test_distill_candidates_multiple()
    print("\nAll distillation tests passed!")
