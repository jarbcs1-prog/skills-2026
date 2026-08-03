"""Tests for master-of-dissent safety filters."""
from scripts.safety import DissentSafety


def test_safety_blocks_personal_appearance():
    safety = DissentSafety()
    result = safety.filter("Your appearance is bad", "personal_appearance")
    assert result.allowed is False


def test_safety_blocks_protected_characteristics():
    safety = DissentSafety()
    result = safety.filter("Comment about race", "protected_characteristics")
    assert result.allowed is False


def test_safety_blocks_mental_health():
    safety = DissentSafety()
    result = safety.filter("Your mental health is questionable", "mental_health")
    assert result.allowed is False


def test_safety_allows_ideas():
    safety = DissentSafety()
    result = safety.filter("Your argument is flawed", "ideas_arguments")
    assert result.allowed is True


def test_safety_allows_code_quality():
    safety = DissentSafety()
    result = safety.filter("This code has bugs", "code_quality")
    assert result.allowed is True


def test_safety_allows_technical_decisions():
    safety = DissentSafety()
    result = safety.filter("The architecture choice is wrong", "technical_decisions")
    assert result.allowed is True


def test_safety_allows_boasting():
    safety = DissentSafety()
    result = safety.filter("Your claim is exaggerated", "boasting_claims")
    assert result.allowed is True


def test_safety_allows_logical_inconsistencies():
    safety = DissentSafety()
    result = safety.filter("That contradicts your earlier point", "logical_inconsistencies")
    assert result.allowed is True


def test_safety_blocked_targets_list():
    safety = DissentSafety()
    assert len(safety.BLOCKED_TARGETS) > 0


def test_safety_allowed_targets_list():
    safety = DissentSafety()
    assert len(safety.ALLOWED_TARGETS) > 0