from __future__ import annotations

from scripts.daydream_config import DEFAULT_CONFIG
from scripts.quality import critique, score_insight

DIMENSIONS = DEFAULT_CONFIG["dimensions"]

PASSING_TEXT = "We should build and implement a new automated system that improves focus per studies."
BLAND_TEXT = "hello world this is a bland text with nothing here"
SOURCE_A = "one two three four five"
SOURCE_B = "six seven eight nine ten"


def test_score_insight_reports_dimensions_and_weighted_in_range() -> None:
    result = score_insight(PASSING_TEXT, SOURCE_A, SOURCE_B, DIMENSIONS)
    for dim in ("novelty", "actionability", "connectivity", "evidence"):
        assert 0.0 <= result[dim] <= 10.0
    assert 0.0 <= result["weighted"] <= 10.0
    assert set(result) >= {"novelty", "actionability", "connectivity", "evidence", "weighted", "passes"}


def test_actionable_insight_passes_threshold() -> None:
    result = score_insight(PASSING_TEXT, SOURCE_A, SOURCE_B, DIMENSIONS)
    assert result["passes"] is True
    assert result["weighted"] >= 7.0


def test_bland_short_text_fails_threshold() -> None:
    result = score_insight(BLAND_TEXT, SOURCE_A, SOURCE_B, DIMENSIONS)
    assert result["passes"] is False
    assert result["weighted"] < 7.0


def test_critique_shape_and_reason() -> None:
    result = critique(PASSING_TEXT, SOURCE_A, SOURCE_B, DIMENSIONS)
    assert isinstance(result["passed"], bool)
    assert set(result["scores"]) >= {"novelty", "actionability", "connectivity", "evidence"}
    assert isinstance(result["reason"], str)
    assert result["reason"]
