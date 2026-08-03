"""Tests for having-difficult-conversations CLI."""
import subprocess
import sys
from pathlib import Path


def test_prepare_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "prepare", "--type", "feedback", "--person", "Alex"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0
    assert "feedback" in result.stdout.lower()


def test_template_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "template", "--type", "feedback"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_practice_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "practice", "--type", "feedback"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_simulate_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "simulate", "--persona", "defensive",
         "--opening", "I need to talk about your performance."],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_log_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "log", "--outcome", "resolved",
         "--person", "Alex"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_history_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "history", "--last", "5"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_analytics_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "analytics", "--month", "2026-01"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0