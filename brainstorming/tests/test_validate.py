"""Tests for scripts.validate_design_doc."""

from __future__ import annotations

from pathlib import Path

from scripts.validate_design_doc import REQUIRED_SECTIONS, validate_design_doc


def _write_doc(path: Path, headings: list[str]) -> Path:
    content = "\n".join(f"## {name}\n\nplaceholder\n" for name in headings)
    path.write_text(content, encoding="utf-8")
    return path


def test_valid_doc(tmp_path):
    doc = _write_doc(tmp_path / "valid.md", REQUIRED_SECTIONS)
    result = validate_design_doc(doc)
    assert result["valid"] is True
    assert result["missing_sections"] == []
    assert result["present_sections"] == REQUIRED_SECTIONS
    assert result["path"] == str(doc)


def test_missing_sections(tmp_path):
    headings = [name for name in REQUIRED_SECTIONS if name not in {"Testing", "Data Flow"}]
    doc = _write_doc(tmp_path / "incomplete.md", headings)
    result = validate_design_doc(doc)
    assert result["valid"] is False
    assert result["missing_sections"] == ["Data Flow", "Testing"]
    assert "Data Flow" not in result["present_sections"]
    assert "Testing" not in result["present_sections"]


def test_headings_case_insensitive(tmp_path):
    doc = tmp_path / "case.md"
    doc.write_text("# Purpose\n\nplaceholder\n### scope\n\nplaceholder\n", encoding="utf-8")
    result = validate_design_doc(doc)
    assert "Purpose" in result["present_sections"]
    assert "Scope" in result["present_sections"]
