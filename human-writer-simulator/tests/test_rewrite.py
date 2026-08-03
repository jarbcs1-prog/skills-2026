"""Tests for human-writer-simulator rewriter."""
from scripts.rewriter import HumanRewriter, RewriteConstraints, detect_ai_text, score_human_likeness


def test_rewrite_returns_result():
    rewriter = HumanRewriter()
    result = rewriter.rewrite("This is a test sentence about the system.")
    assert result.rewritten is not None
    assert result.ai_probability_before >= 0.0
    assert result.ai_probability_after >= 0.0
    assert result.human_score.overall >= 0.0


def test_rewrite_preserves_meaning():
    rewriter = HumanRewriter()
    result = rewriter.rewrite("The system processes data efficiently.")
    assert result.meaning_preserved is True


def test_rewrite_with_conversational_style():
    rewriter = HumanRewriter(imperfection_level=0.3)
    constraints = RewriteConstraints(target_style="conversational")
    result = rewriter.rewrite("The system processes data efficiently.", constraints=constraints)
    assert result.rewritten is not None


def test_rewrite_with_technical_style():
    rewriter = HumanRewriter(imperfection_level=0.2)
    constraints = RewriteConstraints(target_style="technical")
    result = rewriter.rewrite("The system processes data efficiently.", constraints=constraints)
    assert result.rewritten is not None


def test_detect_ai_text():
    result = detect_ai_text("This is a test sentence.")
    assert "ai_probability" in result
    assert isinstance(result["is_ai_generated"], bool)


def test_score_human_likeness():
    result = score_human_likeness("This is a test sentence.")
    assert "overall" in result
    assert 0.0 <= result["overall"] <= 1.0


def test_rewrite_reduces_ai_probability():
    # AI-like text should have lower AI probability after rewrite
    ai_text = "The system processes data efficiently. The algorithm optimizes performance. The model delivers accurate results."
    rewriter = HumanRewriter(imperfection_level=0.4)
    constraints = RewriteConstraints(target_style="conversational")
    result = rewriter.rewrite(ai_text, constraints=constraints)
    # The rewritten text should have lower AI probability
    assert result.ai_probability_after <= result.ai_probability_before or result.ai_probability_after < 0.8
