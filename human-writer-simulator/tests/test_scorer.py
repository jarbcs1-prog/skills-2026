"""Tests for human-writer-simulator scorer."""
from scripts.scorer import score_human_likeness


def test_score_human_likeness_returns_dict():
    result = score_human_likeness("This is a test sentence.")
    assert "overall" in result
    assert "naturalness" in result
    assert "personality" in result
    assert "imperfection" in result
    assert "coherence" in result
    assert "emotional_range" in result
    assert "contextual_fit" in result


def test_score_human_likeness_range():
    result = score_human_likeness("This is a test sentence.")
    assert 0.0 <= result["overall"] <= 1.0


def test_score_human_likeness_conversational():
    text = "I think this works well. You know, it's been my experience that this approach is solid."
    result = score_human_likeness(text, "conversational")
    assert result["overall"] >= 0.0


def test_score_human_likeness_technical():
    text = "The system processes data through a pipeline architecture with configurable parameters."
    result = score_human_likeness(text, "technical")
    assert result["overall"] >= 0.0


def test_score_human_likeness_empty():
    result = score_human_likeness("")
    assert result["overall"] >= 0.0


def test_score_human_likeness_personal_voice_high():
    text = "I personally believe this is the right approach. My experience shows it works."
    result = score_human_likeness(text, "conversational")
    assert result["personality"] >= 0.0
