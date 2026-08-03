"""Tests for trust-psychology CLI."""
import subprocess
import sys
from pathlib import Path


def test_audit_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "audit", "--context", "saas_signup"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_score_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "score", "--url", "https://example.com"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_signals_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "signals", "--list"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_ab_test_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "ab-test", "--control", "current",
         "--treatment", "new_guarantee", "--metric", "conversion"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_components_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "components", "--framework", "react"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_tokens_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "tokens", "--format", "design-md"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0