"""Tests for the code-quality CLI."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run_cli(*args: str, cwd: str | Path | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    return subprocess.run(
        [sys.executable, "-m", "scripts.cli", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(cwd or ROOT),
        env=env,
    )


def test_config_show() -> None:
    result = run_cli("config", "show")
    assert result.returncode == 0
    assert '"languages"' in result.stdout


def test_config_validate() -> None:
    result = run_cli("config", "validate")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["valid"] is True
    assert data["errors"] == []


def test_config_show_invalid_config_file(tmp_path: Path) -> None:
    config_path = tmp_path / "bad.yml"
    config_path.write_text("unknown_key: 1\n", encoding="utf-8")
    result = run_cli("config", "show", "--config", str(config_path))
    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert "errors" in data


def test_incremental() -> None:
    result = run_cli("incremental")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "changed_files" in data
    assert "filtered" in data
    assert "count" in data


def test_init_vscode(tmp_path: Path) -> None:
    result = run_cli("init", "--ide", "vscode", cwd=tmp_path)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert ".vscode/tasks.json" in data["created"]
    tasks = json.loads((tmp_path / ".vscode" / "tasks.json").read_text(encoding="utf-8"))
    assert tasks["tasks"][0]["label"] == "code-quality (agent)"
    assert "finalize" in tasks["tasks"][0]["command"]
    settings = json.loads((tmp_path / ".vscode" / "settings.json").read_text(encoding="utf-8"))
    assert isinstance(settings, dict)
    pre_commit = (tmp_path / ".husky" / "pre-commit").read_text(encoding="utf-8")
    assert pre_commit.startswith("#!/bin/bash")
    assert "finalize" in pre_commit


def test_init_vscode_skips_conflicting_file(tmp_path: Path) -> None:
    (tmp_path / ".vscode").mkdir()
    (tmp_path / ".vscode" / "tasks.json").write_text("custom content", encoding="utf-8")
    result = run_cli("init", "--ide", "vscode", cwd=tmp_path)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert ".vscode/tasks.json" in data["skipped"]
    assert (tmp_path / ".vscode" / "tasks.json").read_text(encoding="utf-8") == "custom content"
