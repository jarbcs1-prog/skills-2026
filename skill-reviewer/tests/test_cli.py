"""Subprocess tests for the skill-reviewer CLI (python -m scripts.cli ...)."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

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


def make_good(tmp_path: Path, name: str = "good-skill") -> Path:
    skill = tmp_path / name
    skill.mkdir()
    (skill / "SKILL.md").write_text(GOOD_SKILL_MD, encoding="utf-8")
    (skill / "scripts").mkdir()
    (skill / "scripts" / "cli.py").write_text("def main(): ...\n", encoding="utf-8")
    (skill / "tests").mkdir()
    (skill / "tests" / "__init__.py").write_text("", encoding="utf-8")
    return skill


def make_bad(tmp_path: Path, name: str = "bad-skill") -> Path:
    skill = tmp_path / name
    skill.mkdir()
    (skill / "SKILL.md").write_text(BAD_SKILL_MD, encoding="utf-8")
    return skill


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "scripts.cli", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_review_good_skill_exits_zero(tmp_path):
    skill = make_good(tmp_path)
    proc = run_cli("review", "--skill", str(skill))
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["passed"] is True


def test_review_bad_skill_exits_one(tmp_path):
    skill = make_bad(tmp_path)
    proc = run_cli("review", "--skill", str(skill))
    assert proc.returncode == 1
    data = json.loads(proc.stdout)
    assert data["passed"] is False


def test_review_batch_exits_one_with_counts(tmp_path):
    make_good(tmp_path, name="alpha")
    make_bad(tmp_path, name="beta")
    proc = run_cli("review", "--skills-dir", str(tmp_path), "--batch")
    assert proc.returncode == 1
    data = json.loads(proc.stdout)
    assert "passed_count" in data
    assert data["total"] == 2
    assert data["passed_count"] == 1


def test_review_batch_writes_csv(tmp_path):
    make_good(tmp_path, name="alpha")
    output = tmp_path / "report.csv"
    proc = run_cli("review", "--skills-dir", str(tmp_path), "--batch", "--output", str(output))
    assert proc.returncode == 0
    assert output.exists()
    data = json.loads(proc.stdout)
    assert data["report"] == str(output)
    assert "path,name,score,passed" in output.read_text(encoding="utf-8")


def test_health_reports_score(tmp_path):
    skill = make_good(tmp_path)
    proc = run_cli("health", "--skill", str(skill))
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["score"] >= 70
    assert data["passed"] is True
    assert data["trend"] == "flat"


def test_evaluate_includes_fixes(tmp_path):
    skill = make_good(tmp_path)
    proc = run_cli("evaluate", "--skill", str(skill))
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["name"] == "my-skill"
    assert data["passed"] is True
    assert "fixes" in data
    assert isinstance(data["fixes"], list)


def test_consistency_report_exits_zero(tmp_path):
    make_good(tmp_path)
    report = ROOT / "skill-reviewer-consistency-report.md"
    try:
        proc = run_cli("consistency", "--skills-dir", str(tmp_path), "--report")
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert "report" in data
        assert data["skills"][0]["consistent"] is True
    finally:
        report.unlink(missing_ok=True)
