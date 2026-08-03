"""Tests for cheaper-reasoning quality module."""
from scripts.quality import ContemplationQuality, QualityScore


def test_score_returns_quality_score():
    q = ContemplationQuality()
    result = q.score("Some contemplation text here.")
    assert isinstance(result, QualityScore)


def test_score_empty_contemplation():
    q = ContemplationQuality()
    result = q.score("")
    assert result.coherence == 0.0
    assert result.progression == 0.0


def test_score_short_contemplation():
    q = ContemplationQuality()
    result = q.score("Brief thought.")
    assert result.weighted_average() >= 0.0


def test_score_long_contemplation():
    q = ContemplationQuality()
    text = " ".join(["This is a longer contemplation with more content to analyze."] * 20)
    result = q.score(text)
    assert result.weighted_average() >= 0.0


def test_quality_score_weighted_average():
    score = QualityScore(coherence=0.8, progression=0.7, self_correction=0.6, insight_density=0.9)
    avg = score.weighted_average()
    assert 0.0 <= avg <= 1.0
    assert abs(avg - 0.75) < 0.01


def test_quality_score_to_dict():
    score = QualityScore(coherence=0.5, progression=0.5, self_correction=0.5, insight_density=0.5)
    d = score.to_dict()
    assert "coherence" in d
    assert "progression" in d
    assert "self_correction" in d
    assert "insight_density" in d
    assert "weighted_average" in d


def test_score_high_coherence():
    q = ContemplationQuality()
    text = "First, I observe that X is true. Therefore, since X implies Y, Y must also hold. Consequently, Z follows from Y."
    result = q.score(text)
    assert result.coherence > 0.3


def test_score_self_correction_detected():
    q = ContemplationQuality()
    text = "I think X is true. Wait, actually, on second thought, maybe I should reconsider. Backtrack: X might not hold."
    result = q.score(text)
    assert result.self_correction > 0.3


def test_score_progression():
    q = ContemplationQuality()
    text = "Starting with basics: A is true. Building on that: B follows from A. This connects to what I observed: C emerges from B."
    result = q.score(text)
    assert result.progression > 0.3


def test_score_insight_density():
    q = ContemplationQuality()
    text = "A" * 5000
    result = q.score(text)
    assert result.insight_density > 0.3