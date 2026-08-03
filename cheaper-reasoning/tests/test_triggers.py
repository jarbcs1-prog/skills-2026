"""Tests for cheaper-reasoning triggers module."""
from scripts.triggers import should_use_deep_reasoning, Task, ReasoningDecision


def test_no_triggers_returns_false():
    task = Task(complexity_score=0.3, uncertainty_level=0.2)
    result = should_use_deep_reasoning(task)
    assert result.use is False


def test_high_complexity_triggers():
    task = Task(complexity_score=0.8, uncertainty_level=0.3)
    result = should_use_deep_reasoning(task)
    assert result.use is True
    assert result.reason == "high_complexity"


def test_high_uncertainty_triggers():
    task = Task(complexity_score=0.3, uncertainty_level=0.9)
    result = should_use_deep_reasoning(task)
    assert result.use is True
    assert result.reason == "high_uncertainty"


def test_architecture_decision_triggers():
    task = Task(requires_architecture_decision=True)
    result = should_use_deep_reasoning(task)
    assert result.use is True
    assert result.reason == "architecture_decision"


def test_conflicting_constraints_triggers():
    task = Task(has_conflicting_constraints=True)
    result = should_use_deep_reasoning(task)
    assert result.use is True
    assert result.reason == "conflicting_constraints"


def test_explicit_request_triggers():
    task = Task(user_explicitly_requested_reasoning=True)
    result = should_use_deep_reasoning(task)
    assert result.use is True
    assert result.reason == "explicit_request"
    assert result.confidence == 1.0


def test_multiple_triggers_picks_highest_confidence():
    task = Task(complexity_score=0.8, uncertainty_level=0.9, user_explicitly_requested_reasoning=True)
    result = should_use_deep_reasoning(task)
    assert result.use is True
    assert result.confidence == 1.0


def test_all_triggers_false():
    task = Task(complexity_score=0.1, uncertainty_level=0.1, requires_architecture_decision=False, has_conflicting_constraints=False, user_explicitly_requested_reasoning=False)
    result = should_use_deep_reasoning(task)
    assert result.use is False