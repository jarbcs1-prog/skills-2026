"""Tests for systematic-debugging CLI."""
import subprocess
import sys
from pathlib import Path


def test_start_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "start", "--error", "TypeError", "--test", "pytest test_x.py"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0
    assert "TypeError" in result.stdout


def test_worksheet_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "worksheet", "--output", "test-worksheet.md"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_evidence_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "evidence", "--component", "api", "--input", "req", "--output", "resp"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_trace_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "trace", "--variable", "user_id", "--from", "main.py:10"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_hypothesis_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "hypothesis", "--add", "null pointer", "--test", "mock auth"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_pattern_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "pattern", "--search", "null", "--language", "python"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_report_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "report", "--format", "markdown", "--output", "test-report.md"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0