"""Tests for scripts.spec_diff."""

from __future__ import annotations


from scripts import spec_diff


def test_diff_design_docs(tmp_path):
    base = tmp_path / "base.md"
    target = tmp_path / "target.md"
    base.write_text("# A\n## B\n## C\n", encoding="utf-8")
    target.write_text("## B\n## C\n## D\n", encoding="utf-8")
    result = spec_diff.diff_design_docs(base, target)
    assert result["base"] == str(base)
    assert result["target"] == str(target)
    assert result["added_sections"] == ["D"]
    assert result["removed_sections"] == ["A"]
    assert result["changed"] is True


def test_diff_unchanged(tmp_path):
    base = tmp_path / "base.md"
    target = tmp_path / "target.md"
    base.write_text("## B\n## C\n", encoding="utf-8")
    target.write_text("## B\n## C\n", encoding="utf-8")
    result = spec_diff.diff_design_docs(base, target)
    assert result["added_sections"] == []
    assert result["removed_sections"] == []
    assert result["changed"] is False
