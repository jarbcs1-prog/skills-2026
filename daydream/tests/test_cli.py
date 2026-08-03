from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

os.environ.setdefault("PYTHONPATH", str(ROOT))

VAULT_NOTES = {
    "build.md": "Build tools improve work. data shows automate tasks apply methods. Build tools improve work. data shows automate tasks apply methods.",
    "implement.md": "Implement systems adopt data. studies show improve use automation. Implement systems adopt data. studies show improve use automation.",
    "automate.md": "Automate workflows build systems. studies show data improves focus. Automate workflows build systems. studies show data improves focus.",
}


def run_cli(*args: str, cwd: str | Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "scripts.cli", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=cwd or str(ROOT),
    )


def _make_vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    vault.mkdir()
    for name, text in VAULT_NOTES.items():
        (vault / name).write_text(text, encoding="utf-8")
    return vault


def test_run_writes_insights(tmp_path: Path) -> None:
    _make_vault(tmp_path)
    result = run_cli("run", "--vault", "vault", "--pairs", "5", "--seed", "1", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["insights_generated"] >= 0
    assert payload["insights_passed"] >= 1
    assert payload["written"] >= 1
    assert (tmp_path / "Daydreams").is_dir()
    assert list((tmp_path / "Daydreams").glob("*.md"))


def test_run_dry_run_writes_nothing(tmp_path: Path) -> None:
    _make_vault(tmp_path)
    result = run_cli("run", "--vault", "vault", "--pairs", "5", "--seed", "1", "--dry-run", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["written"] == 0
    assert not (tmp_path / "Daydreams").exists()


def test_config_show(tmp_path: Path) -> None:
    result = run_cli("config", "show", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert "sampling" in result.stdout


def test_dedup_exits_zero(tmp_path: Path) -> None:
    _make_vault(tmp_path)
    result = run_cli("dedup", "--vault", "vault", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["pairs"] == []


def test_graph_exits_zero_and_writes_graphml(tmp_path: Path) -> None:
    _make_vault(tmp_path)
    result = run_cli("graph", "--vault", "vault", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["notes"] == 3
    assert (tmp_path / ".daydream_graph.graphml").is_file()


def test_stats_exits_zero(tmp_path: Path) -> None:
    _make_vault(tmp_path)
    run_cli("run", "--vault", "vault", "--pairs", "5", "--seed", "1", cwd=tmp_path)
    result = run_cli("stats", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["runs"] == 1
    assert payload["total_insights"] >= 1
    assert payload["avg_score"] >= 0.0
