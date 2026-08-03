"""Unit tests for the skill-reviewer review engine."""

from pathlib import Path

from scripts.skill_reviewer import (
    DIMENSIONS,
    REQUIRED_SECTIONS,
    check_consistency,
    generate_fixes,
    review_skill,
    score_description,
    validate_structure,
)

GOOD_SKILL_MD = """\
---
name: my-skill
description: Automates PDF text extraction and form parsing. Use when processing PDF documents, filling forms or extracting tables from scanned files.
---

# My Skill

## Description
Extracts text and tables from PDF documents, fills interactive forms and converts scanned files to searchable markdown.

## When to use
Use when the user mentions PDFs, forms, document extraction or scanned files that need OCR.

## Workflow
1. Read the input PDF with `scripts/cli.py`.
2. Extract text and tables.
3. Verify output by running the tests in the tests directory.

## Input
A path to a PDF file or a directory of PDF files.

## Output
Markdown text plus extracted tables, written to stdout.

## Notes
Run the tests in the tests directory before shipping.
"""

BAD_SKILL_MD = """\
# A skill with no structure

This fixture fails every structural check on purpose.

password = "sup3rsecret1"

It has no sections, no frontmatter and leaks a credential.

This extra filler line keeps the file comfortably above ten lines so that only
the structural checks trip, which makes the failure mode easy to reason about.
"""


def build_good(tmp_path: Path, name: str = "good-skill") -> Path:
    skill = tmp_path / name
    skill.mkdir()
    (skill / "SKILL.md").write_text(GOOD_SKILL_MD, encoding="utf-8")
    (skill / "scripts").mkdir()
    (skill / "scripts" / "cli.py").write_text("def main(): ...\n", encoding="utf-8")
    (skill / "tests").mkdir()
    (skill / "tests" / "test_thing.py").write_text("def test_x():\n    pass\n", encoding="utf-8")
    return skill


def build_bad(tmp_path: Path, name: str = "bad-skill") -> Path:
    skill = tmp_path / name
    skill.mkdir()
    (skill / "SKILL.md").write_text(BAD_SKILL_MD, encoding="utf-8")
    return skill


def test_dimensions_total_100():
    assert sum(DIMENSIONS.values()) == 100


def test_required_sections():
    assert len(REQUIRED_SECTIONS) == 6


def test_review_good_skill_passes(tmp_path):
    skill = build_good(tmp_path)
    review = review_skill(skill)
    assert review["score"] >= 70
    assert review["passed"] is True
    assert review["structure"]["valid"] is True
    assert review["security"]["vulnerabilities"] == []
    assert review["consistency"]["consistent"] is True


def test_review_good_skill_dimension_breakdown(tmp_path):
    skill = build_good(tmp_path)
    review = review_skill(skill)
    dimensions = review["dimensions"]
    assert dimensions["description"] == 20
    assert dimensions["structure"] == 20
    assert dimensions["workflow"] == 15
    assert dimensions["safety"] == 10
    assert dimensions["tests"] == 20
    assert sum(dimensions.values()) == review["score"]


def test_review_bad_skill_fails(tmp_path):
    skill = build_bad(tmp_path)
    review = review_skill(skill)
    assert review["passed"] is False
    assert review["structure"]["valid"] is False
    assert len(review["security"]["vulnerabilities"]) > 0
    assert len(review["fixes"]) > 0


def test_validate_structure_good(tmp_path):
    skill = build_good(tmp_path)
    structure = validate_structure(skill)
    assert structure["valid"] is True
    assert all(structure["checks"].values())
    assert structure["score"] == 20
    assert structure["errors"] == []


def test_validate_structure_bad(tmp_path):
    skill = build_bad(tmp_path)
    structure = validate_structure(skill)
    assert structure["valid"] is False
    assert structure["checks"]["frontmatter"] is False
    assert structure["checks"]["sections"] is False
    assert structure["score"] < 20


def test_validate_structure_missing_skill_md(tmp_path):
    structure = validate_structure(tmp_path)
    assert structure["valid"] is False
    assert structure["score"] == 0


def test_score_description():
    assert score_description("") == 0
    assert score_description("Short") == 5
    good = "Automates PDF text extraction. Use when processing PDF documents or extracting tables."
    assert score_description(good) == 20
    no_trigger = "Automates PDF text extraction and form parsing."
    assert score_description(no_trigger) == 15
    boilerplate = "I am an AI assistant that helps with tasks. Use when you need assistance."
    assert score_description(boilerplate) < 20


def test_check_consistency_missing_reference(tmp_path):
    skill = build_good(tmp_path)
    skill_md = skill / "SKILL.md"
    skill_md.write_text(
        skill_md.read_text(encoding="utf-8") + "\nSee `references/checklist.md` for details.\n",
        encoding="utf-8",
    )
    result = check_consistency(skill)
    assert "references/checklist.md" in result["missing_references"]
    assert result["consistent"] is False


def test_check_consistency_requires_tests_when_mentioned(tmp_path):
    skill = tmp_path / "solo"
    skill.mkdir()
    skill_md = "\n".join(
        [
            "---",
            "name: solo",
            "description: Does a thing. Use when doing a thing.",
            "---",
            "",
            "# Solo",
            "## Workflow",
            "1. Run the tests to verify behaviour.",
        ]
    )
    (skill / "SKILL.md").write_text(skill_md, encoding="utf-8")
    result = check_consistency(skill)
    assert "tests/" in result["missing_references"]
    assert result["consistent"] is False


def test_generate_fixes():
    review = {
        "description_score": 10,
        "structure": {"checks": {"frontmatter": False}},
        "consistency": {"missing_references": ["references/checklist.md"]},
        "content": "A minimal description with no numbered steps.",
    }
    fixes = generate_fixes(review)
    assert any("description" in fix for fix in fixes)
    assert any("Workflow" in fix for fix in fixes)
    assert any("references/checklist.md" in fix for fix in fixes)
    assert any("frontmatter" in fix for fix in fixes)


def test_generate_fixes_empty_for_clean_review(tmp_path):
    skill = build_good(tmp_path)
    fixes = generate_fixes(review_skill(skill))
    assert fixes == []
