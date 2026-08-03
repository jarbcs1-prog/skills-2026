"""Tests for scripts.init_skill."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_init(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "init_skill.py"), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(cwd or ROOT),
    )


def test_init_creates_skill_directory(tmp_path: Path) -> None:
    result = run_init("my-test-skill", "--target-dir", str(tmp_path))
    assert result.returncode == 0, result.stderr
    skill_dir = tmp_path / "my-test-skill"
    assert (skill_dir / "SKILL.md").exists()
    assert (skill_dir / "scripts" / "__init__.py").exists()
    assert (skill_dir / "references" / "overview.md").exists()
    assert (skill_dir / "templates" / "README.md").exists()


def test_init_rejects_existing_directory(tmp_path: Path) -> None:
    (tmp_path / "exists-skill").mkdir()
    result = run_init("exists-skill", "--target-dir", str(tmp_path))
    assert result.returncode == 1
    assert "already exists" in result.stderr


def test_init_rejects_invalid_name(tmp_path: Path) -> None:
    result = run_init("INVALID Name!", "--target-dir", str(tmp_path))
    assert result.returncode == 1
    assert "invalid characters" in result.stderr.lower()


def test_init_sanitizes_name(tmp_path: Path) -> None:
    result = run_init("My Cool Skill", "--target-dir", str(tmp_path))
    assert result.returncode == 0
    assert (tmp_path / "my-cool-skill").exists()
