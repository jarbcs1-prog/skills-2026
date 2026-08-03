"""Tests for writing-plans CLI."""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "scripts.cli", *args],
        capture_output=True, text=True,
        cwd=str(ROOT),
    )


def make_plan(tmp: str) -> Path:
    result = run_cli("init", "--template", "feature", "--name", "user authentication", "--goal", "Add login", "--output", tmp)
    assert result.returncode == 0, result.stderr
    candidates = list(Path(tmp).glob("*-user-authentication.md"))
    assert candidates
    return candidates[0]


def test_init_command():
    with tempfile.TemporaryDirectory() as tmp:
        result = run_cli("init", "--template", "feature", "--name", "user authentication", "--output", tmp)
        assert result.returncode == 0, result.stderr
        plan_files = list(Path(tmp).glob("*.md"))
        assert len(plan_files) == 1
        assert "user authentication" in plan_files[0].read_text(encoding="utf-8")


def test_init_unknown_template_fails():
    result = run_cli("init", "--template", "nope", "--name", "x")
    assert result.returncode != 0


def test_validate_command():
    with tempfile.TemporaryDirectory() as tmp:
        plan = make_plan(tmp)
        result = run_cli("validate", "--plan", str(plan))
        assert result.returncode == 0, result.stderr
        assert "score=" in result.stdout


def test_validate_missing_file_fails():
    result = run_cli("validate", "--plan", "does-not-exist.md")
    assert result.returncode != 0


def test_extract_tasks_command():
    with tempfile.TemporaryDirectory() as tmp:
        plan = make_plan(tmp)
        result = run_cli("extract-tasks", "--plan", str(plan), "--format", "subagent")
        assert result.returncode == 0, result.stderr
        assert "Task 1" in result.stdout


def test_compose_command():
    with tempfile.TemporaryDirectory() as tmp:
        p1 = make_plan(tmp)
        result = run_cli("compose", "--plans", f"{p1},{p1}", "--name", "combined", "--output", tmp)
        assert result.returncode == 0, result.stderr
        composed = list(Path(tmp).glob("*-combined.md"))
        assert len(composed) == 1
        assert composed[0].read_text(encoding="utf-8").count("## Task ") >= 6


def test_version_command():
    with tempfile.TemporaryDirectory() as tmp:
        plan = make_plan(tmp)
        result = run_cli("version", "--plan", str(plan), "--bump", "minor")
        assert result.returncode == 0, result.stderr
        assert "**Version:** 0.2.0" in plan.read_text(encoding="utf-8")


def test_track_command():
    with tempfile.TemporaryDirectory() as tmp:
        plan = make_plan(tmp)
        result = run_cli("track", "--plan", str(plan), "--status")
        assert result.returncode == 0, result.stderr
        assert "pending" in result.stdout
        result = run_cli("track", "--plan", str(plan), "--task", "1", "--set", "done")
        assert result.returncode == 0, result.stderr
        result = run_cli("track", "--plan", str(plan), "--status")
        assert "done" in result.stdout


def test_sync_command():
    with tempfile.TemporaryDirectory() as tmp:
        plan = make_plan(tmp)
        result = run_cli("sync", "--plan", str(plan), "--project", str(ROOT), "--commits")
        assert result.returncode == 0, result.stderr
        assert "Task " in result.stdout


def test_no_command_fails():
    result = run_cli()
    assert result.returncode != 0
