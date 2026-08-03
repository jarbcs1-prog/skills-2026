"""Tests for scripts.templates."""
from __future__ import annotations

import pytest

from scripts.templates import TEMPLATE_TYPES, render_template


def test_template_type_count():
    assert len(TEMPLATE_TYPES) >= 10


def test_render_template_fills_topic():
    content = render_template("market_entry", "enterprise AI market entry")
    assert "enterprise AI market entry" in content
    assert content.startswith("# ")


def test_render_template_with_params():
    content = render_template("market_entry", "X", {"note": "hi"})
    assert "# X" in content


def test_render_template_unknown_raises():
    with pytest.raises(KeyError):
        render_template("nope", "X")


def test_all_templates_structured():
    for template_type, template in TEMPLATE_TYPES.items():
        assert "## " in template, template_type
        assert "{topic}" in template, template_type
