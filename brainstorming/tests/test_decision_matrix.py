"""Tests for scripts.decision_matrix."""

from __future__ import annotations

from scripts import decision_matrix


def test_evaluate_winner_and_ranking():
    options = ["build", "buy", "partner"]
    criteria = ["cost", "time", "risk"]
    weights = [0.4, 0.3, 0.3]
    result = decision_matrix.evaluate(options, criteria, weights)
    scores = result["scores"]
    assert result["ranking"] == sorted(options, key=lambda o: scores[o], reverse=True)
    assert result["winner"] == max(scores, key=lambda o: scores[o])
    assert result["winner"] == result["ranking"][0]


def test_sensitivity_keys_present():
    result = decision_matrix.evaluate(["build", "buy"], ["cost", "time"], [0.5, 0.5])
    for option in ("build", "buy"):
        assert "low" in result["sensitivity"][option]
        assert "high" in result["sensitivity"][option]
        assert result["sensitivity"][option]["low"] < result["sensitivity"][option]["high"]


def test_evaluate_deterministic():
    options = ["build", "buy", "partner"]
    criteria = ["cost", "time", "risk"]
    weights = [0.4, 0.3, 0.3]
    first = decision_matrix.evaluate(options, criteria, weights)
    second = decision_matrix.evaluate(options, criteria, weights)
    assert first == second


def test_evaluate_with_scores_matrix():
    options = ["build", "buy"]
    criteria = ["cost", "time"]
    weights = [0.5, 0.5]
    matrix = [[10.0, 1.0], [1.0, 10.0]]
    result = decision_matrix.evaluate(options, criteria, weights, scores_matrix=matrix)
    assert result["winner"] == "build"
    assert result["scores"]["build"] == result["scores"]["buy"]
    assert result["ranking"] == ["build", "buy"]


def test_evaluate_rejects_mismatched_weights():
    try:
        decision_matrix.evaluate(["build"], ["cost", "time"], [0.5])
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for mismatched weights")
