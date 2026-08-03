"""Tests for test-driven-development CLI."""
import subprocess
import sys
from pathlib import Path


def test_new_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "new", "--feature", "retry logic", "--language", "python"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_red_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "red", "--test", "tests/test_auth.py::test_login"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_green_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "green", "--implement", "src/auth.py"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_refactor_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "refactor", "--clean", "src/auth.py"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_cycle_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "cycle", "--test", "tests/test_auth.py", "--implement", "src/auth.py"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_verify_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "verify", "--coverage", "80", "--mutation"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_coach_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "coach", "--mode", "strict", "--language", "python"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_stats_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "stats", "--project", ".", "--period", "30d"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0