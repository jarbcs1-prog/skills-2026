"""Tests for scripts.validate_skill."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_validate(skill_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_skill.py"), str(skill_dir)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _create_valid_skill(tmp_path: Path) -> Path:
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: test-skill\ndescription: A test skill.\n---\n# Test Skill\n\n## Workflow\n\n### Step 1: Setup\n\nSetup.\n",
        encoding="utf-8",
    )
    (skill_dir / "scripts").mkdir()
    (skill_dir / "scripts" / "__init__.py").write_text("", encoding="utf-8")
    (skill_dir / "references").mkdir()
    (skill_dir / "references" / "overview.md").write_text("# Overview\n", encoding="utf-8")
    (skill_dir / "templates").mkdir()
    return skill_dir


def test_validate_good_skill_passes(tmp_path: Path) -> None:
    skill_dir = _create_valid_skill(tmp_path)
    result = run_validate(skill_dir)
    assert result.returncode == 0, result.stderr


def test_validate_missing_skill_md_fails(tmp_path: Path) -> None:
    skill_dir = tmp_path / "bad-skill"
    skill_dir.mkdir()
    result = run_validate(skill_dir)
    assert result.returncode == 1
    assert "SKILL.md not found" in result.stderr


def test_validate_invalid_name_fails(tmp_path: Path) -> None:
    skill_dir = tmp_path / "bad-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\ndescription: Missing name field\n---\n# Bad\n",
        encoding="utf-8",
    )
    result = run_validate(skill_dir)
    assert result.returncode == 1
    assert "name" in result.stderr.lower()


def test_validate_python_syntax_error(tmp_path: Path) -> None:
    skill_dir = _create_valid_skill(tmp_path)
    (skill_dir / "scripts" / "bad.py").write_text("def broken(:\n", encoding="utf-8")
    result = run_validate(skill_dir)
    assert result.returncode == 1
    assert "syntax" in result.stderr.lower()
