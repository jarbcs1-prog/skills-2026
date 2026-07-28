"""
Tests for analysis module.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis import (
    reflection_statistics,
    capability_statistics,
    validation_statistics,
)


def test_reflection_statistics_empty():
    stats = reflection_statistics()
    assert stats["total_reflections"] == 0
    assert stats["average_confidence"] == 0
    assert stats["average_evidence"] == 0
    print("PASS: reflection_statistics empty")


def test_capability_statistics_empty():
    stats = capability_statistics()
    assert stats["total_capabilities"] == 0
    assert stats["active_capabilities"] == 0
    assert stats["promotion_levels"] == {}
    print("PASS: capability_statistics empty")


def test_validation_statistics_empty():
    stats = validation_statistics()
    assert stats["total_validations"] == 0
    assert stats["successful_validations"] == 0
    assert stats["success_rate"] == 0
    print("PASS: validation_statistics empty")


if __name__ == "__main__":
    test_reflection_statistics_empty()
    test_capability_statistics_empty()
    test_validation_statistics_empty()
    print("\nAll analysis tests passed!")
