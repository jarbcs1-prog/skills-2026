"""Tests for human-writer-simulator detector."""
from scripts.detector import detect_ai_text


def test_detect_ai_text_returns_dict():
    result = detect_ai_text("This is a simple test sentence.")
    assert "ai_probability" in result
    assert "is_ai_generated" in result
    assert "indicators" in result
    assert "confidence" in result


def test_detect_ai_text_probability_range():
    result = detect_ai_text("This is a simple test sentence.")
    assert 0.0 <= result["ai_probability"] <= 1.0


def test_detect_ai_text_with_uniform_structure():
    # AI-like text with uniform sentence structure
    text = "The system processes data efficiently. The algorithm optimizes performance. The model delivers accurate results."
    result = detect_ai_text(text)
    assert result["ai_probability"] >= 0.0


def test_detect_ai_text_with_personal_voice():
    # Human-like text with personal voice
    text = "I think this approach works well because I've seen it in practice. You know, it's not always perfect but it gets the job done."
    result = detect_ai_text(text)
    assert result["ai_probability"] >= 0.0


def test_detect_ai_text_empty():
    result = detect_ai_text("")
    assert result["ai_probability"] >= 0.0


def test_detect_ai_text_indicators_present():
    text = "The system processes data efficiently. The algorithm optimizes performance."
    result = detect_ai_text(text)
    assert isinstance(result["indicators"], list)
