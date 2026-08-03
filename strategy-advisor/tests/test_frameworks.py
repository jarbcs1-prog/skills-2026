"""Tests for scripts.frameworks."""
from __future__ import annotations

import pytest

from scripts.frameworks import FRAMEWORKS, analyze, get_framework, render_markdown


def test_framework_count():
    assert len(FRAMEWORKS) >= 6


def test_swot_has_four_dimensions():
    assert len(FRAMEWORKS["swot"]["dimensions"]) == 4


def test_get_framework_known():
    framework = get_framework("swot")
    assert framework["id"] == "swot"
    assert framework["name"] == "SWOT Analysis"


def test_get_framework_unknown_raises():
    with pytest.raises(KeyError):
        get_framework("nope")


def test_analyze_returns_dimensions_with_prompts():
    result = analyze("swot", "enterprise AI market entry")
    assert result["framework"] == "swot"
    assert result["topic"] == "enterprise AI market entry"
    assert len(result["dimensions"]) == 4
    for dim in result["dimensions"]:
        assert dim["question"]
        assert len(dim["prompts"]) >= 3
        assert dim["analysis"] == ""


def test_analyze_with_inputs():
    result = analyze("swot", "t", {"Strengths": "strong team"})
    strengths = [d for d in result["dimensions"] if d["name"] == "Strengths"][0]
    assert strengths["analysis"] == "strong team"


def test_render_markdown_contains_topic():
    result = analyze("swot", "enterprise AI market entry")
    markdown = render_markdown("swot", "enterprise AI market entry", result)
    assert "enterprise AI market entry" in markdown
    assert "SWOT Analysis" in markdown


def test_render_markdown_unknown_raises():
    result = analyze("swot", "t")
    with pytest.raises(KeyError):
        render_markdown("nope", "t", result)
