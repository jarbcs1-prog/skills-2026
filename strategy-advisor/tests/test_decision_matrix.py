"""Tests for scripts.decision_matrix."""
from __future__ import annotations

import pytest

from scripts.decision_matrix import DecisionMatrix


def test_evaluate_ranking_and_winner():
    matrix = DecisionMatrix(["a", "b", "c"], ["cost", "time", "risk"])
    result = matrix.evaluate()
    scores = result["scores"]
    assert result["ranking"] == sorted(["a", "b", "c"], key=lambda o: scores[o], reverse=True)
    assert result["winner"] == result["ranking"][0]
    assert result["winner"] == max(scores, key=lambda o: scores[o])


def test_normalized_values_in_unit_range():
    matrix = DecisionMatrix(["a", "b", "c"], ["cost", "time"])
    result = matrix.evaluate()
    for option in matrix.options:
        for value in result["normalized"][option]:
            assert 0.0 <= value <= 1.0


def test_explicit_scores_respected():
    matrix = DecisionMatrix(["a", "b"], ["cost", "time"])
    result = matrix.evaluate(scores={"a": [10.0, 10.0], "b": [5.0, 5.0]})
    assert result["winner"] == "a"
    assert result["scores"]["a"] > result["scores"]["b"]
    assert result["normalized"]["a"] == [1.0, 1.0]
    assert result["normalized"]["b"] == [0.0, 0.0]


def test_weights_change_outcome():
    scores = {"a": [10.0, 1.0], "b": [1.0, 10.0]}
    cost_weighted = DecisionMatrix(["a", "b"], ["cost", "time"], [1.0, 0.0])
    time_weighted = DecisionMatrix(["a", "b"], ["cost", "time"], [0.0, 1.0])
    assert cost_weighted.evaluate(scores)["winner"] == "a"
    assert time_weighted.evaluate(scores)["winner"] == "b"


def test_sensitivity_analysis_structure():
    matrix = DecisionMatrix(["a", "b"], ["cost", "time"], [0.5, 0.5])
    result = matrix.sensitivity_analysis()
    assert len(result["perturbations"]) == 2
    for perturbation in result["perturbations"]:
        assert "-step" in perturbation
        assert "+step" in perturbation
        assert isinstance(perturbation["winner_change"], bool)
    assert isinstance(result["stable_winner"], bool)


def test_evaluate_with_sensitivity_combines():
    matrix = DecisionMatrix(["a", "b"], ["cost", "time"], [0.5, 0.5])
    result = matrix.evaluate_with_sensitivity()
    assert "scores" in result
    assert "winner" in result
    assert "sensitivity" in result
    assert len(result["sensitivity"]["perturbations"]) == 2


def test_weight_mismatch_raises():
    with pytest.raises(ValueError):
        DecisionMatrix(["a", "b"], ["cost", "time"], [0.5])


def test_missing_scores_raises():
    matrix = DecisionMatrix(["a", "b"], ["cost", "time"])
    with pytest.raises(ValueError):
        matrix.evaluate(scores={"a": [1.0, 1.0]})
