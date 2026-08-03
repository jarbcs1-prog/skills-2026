from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "scripts.cli", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(ROOT),
    )


def _make_conversation(path: Path) -> None:
    data = {
        "conversation_id": "cli-test",
        "messages": [{"role": "user", "content": "How should we handle the deployment pipeline?"}],
        "summary": "Discussed the deployment pipeline design.",
    }
    path.write_text(json.dumps(data), encoding="utf-8")


def test_cli_workflow(tmp_path) -> None:
    cache = tmp_path / "cache"
    conversation_path = tmp_path / "conv.json"
    _make_conversation(conversation_path)

    result = run_cli("add", "--conversation", str(conversation_path), "--cache", str(cache))
    assert result.returncode == 0

    result = run_cli("search", "deployment", "--cache", str(cache))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "results" in data

    result = run_cli("summarize", "--conversation-id", "cli-test", "--cache", str(cache))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["summary"] == "Discussed the deployment pipeline design."

    result = run_cli("summarize", "--conversation-id", "nope", "--cache", str(cache))
    assert result.returncode == 1

    output = tmp_path / "export.md"
    result = run_cli("export", "--format", "markdown", "--output", str(output), "--cache", str(cache))
    assert result.returncode == 0


def test_cli_sync_missing_export_dir(tmp_path) -> None:
    result = run_cli("sync", "--export-dir", str(tmp_path / "missing"), "--cache", str(tmp_path / "cache"))
    assert result.returncode == 1
