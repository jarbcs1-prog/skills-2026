"""Tests for dynamic-context-pruning CLI."""
import subprocess
import sys
from pathlib import Path


def test_monitor_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "monitor", "--config", ".agent_context_config.json"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_compact_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "compact", "--context", "history.json", "--output", "compacted.json"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_summarize_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "summarize", "--context", "history.json", "--schema", "agent_default"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_offload_command():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "offload", "--data", "context.json", "--metadata", "meta.json"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_kv_cache_validate():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "kv-cache", "--validate"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_kv_cache_fix():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "kv-cache", "--fix"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_thresholds_show():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "thresholds", "--show"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0


def test_thresholds_update():
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", "thresholds", "--update", "--config", ".agent_context_config.json"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0