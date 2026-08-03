"""Tests for systematic-debugging bug pattern library."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.patterns import BUG_PATTERNS, search_patterns, get_pattern


def test_null_pointer_pattern_exists():
    pattern = get_pattern("null_pointer")
    assert pattern is not None
    assert any("NoneType" in s for s in pattern.symptoms)


def test_off_by_one_pattern_exists():
    pattern = get_pattern("off_by_one")
    assert pattern is not None
    assert any("IndexError" in s for s in pattern.symptoms)


def test_race_condition_pattern_exists():
    pattern = get_pattern("race_condition")
    assert pattern is not None
    assert any("intermittent" in s.lower() for s in pattern.symptoms)


def test_memory_leak_pattern_exists():
    pattern = get_pattern("memory_leak")
    assert pattern is not None
    assert any("growing memory" in s.lower() for s in pattern.symptoms)


def test_search_patterns_finds_by_name():
    results = search_patterns("null pointer")
    assert len(results) > 0
    assert any(r.name == "Null Pointer / None Access" for r in results)


def test_search_patterns_finds_by_symptom():
    results = search_patterns("IndexError")
    assert len(results) > 0


def test_all_patterns_have_required_fields():
    for name, pattern in BUG_PATTERNS.items():
        assert pattern.name, f"{name} missing name"
        assert len(pattern.symptoms) > 0, f"{name} missing symptoms"
        assert len(pattern.common_causes) > 0, f"{name} missing causes"
        assert len(pattern.investigation) > 0, f"{name} missing investigation"
        assert len(pattern.fix_patterns) > 0, f"{name} missing fix patterns"