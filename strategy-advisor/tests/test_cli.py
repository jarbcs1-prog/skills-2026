"""Subprocess tests for scripts.cli."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "scripts.cli", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(ROOT),
    )


def test_analyze_swot():
    result = run_cli("analyze", "--framework", "swot", "--topic", "AI market entry")
    assert result.returncode == 0
    assert "Strengths" in result.stdout


def test_analyze_unknown_framework():
    result = run_cli("analyze", "--framework", "nope", "--topic", "t")
    assert result.returncode == 1


def test_decide_with_weights():
    result = run_cli(
        "decide",
        "--options",
        "a,b",
        "--criteria",
        "cost,time",
        "--weights",
        "0.5,0.5",
    )
    assert result.returncode == 0
    assert "winner" in result.stdout


def test_decide_weight_mismatch():
    result = run_cli("decide", "--options", "a,b", "--criteria", "cost,time", "--weights", "0.5")
    assert result.returncode == 1


def test_scenario_with_variables():
    result = run_cli("scenario", "--strategy", "test", "--variables", "growth=0.1")
    assert result.returncode == 0
    assert "scenarios" in result.stdout


def test_scenario_monte_carlo():
    result = run_cli(
        "scenario",
        "--strategy",
        "test",
        "--variables",
        "growth=0.1",
        "--monte-carlo",
        "--iterations",
        "100",
    )
    assert result.returncode == 0
    assert "monte_carlo" in result.stdout


def test_template_market_entry():
    result = run_cli("template", "--type", "market_entry", "--topic", "X")
    assert result.returncode == 0
    assert "# " in result.stdout


def test_template_unknown_type():
    result = run_cli("template", "--type", "nope", "--topic", "X")
    assert result.returncode == 1


def test_monitor():
    result = run_cli("monitor", "--strategy", "s", "--kpis", "a,b")
    assert result.returncode == 0
    assert '"kpis"' in result.stdout
