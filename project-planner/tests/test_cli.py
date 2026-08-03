"""Tests for project-planner CLI."""
import subprocess
import sys
from pathlib import Path


def test_init_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "init", "--template", "web_app", "--name", "TestProject"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0
    assert "TestProject" in result.stdout


def test_generate_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "generate", "--template", "web_app", "--name", "TestProject"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_schedule_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "schedule", "--plan", "plan.md", "--critical-path"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_track_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "track", "--plan", "plan.md", "--update", "T1:done"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_report_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "report", "--plan", "plan.md", "--format", "burndown"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_export_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "export", "--plan", "plan.md", "--format", "github-projects"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_replan_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "replan", "--plan", "plan.md", "--changes", "changes.json"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_unknown_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "unknown"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode != 0