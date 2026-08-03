from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_cli(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    import os

    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    return subprocess.run(
        [sys.executable, "-m", "scripts.cli", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(cwd or ROOT),
        env=full_env,
        check=False,
    )


def _write_sample(cwd: Path) -> Path:
    bad = cwd / "app.py"
    bad.write_text(
        'query = f"SELECT * FROM users WHERE id = {user_id}"\n'
        "element.innerHTML = user_input\n"
        'api_key = "sk-abcdefghijklmnopqrstuvwxyz"\n',
        encoding="utf-8",
    )
    return bad


def test_review_files_json(tmp_path: Path):
    bad = _write_sample(tmp_path)
    result = run_cli("review", "--files", str(bad), "--cwd", str(tmp_path))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["files_scanned"] == [str(bad)]
    assert data["summary"]["total_findings"] >= 2


def test_review_clean_file():
    result = run_cli("review", "--files", str(ROOT / "scripts" / "__init__.py"))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["summary"]["total_findings"] == 0


def test_review_missing_file_no_crash(tmp_path: Path):
    result = run_cli("review", "--files", str(tmp_path / "missing.py"))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["files_scanned"] == []
    assert data["summary"]["total_findings"] == 0


def test_review_ci_gate_fails(tmp_path: Path):
    bad = _write_sample(tmp_path)
    result = run_cli(
        "review",
        "--files",
        str(bad),
        "--cwd",
        str(tmp_path),
        "--ci",
        "--max-critical",
        "0",
    )
    assert result.returncode == 1
    assert "GATE FAILED" in result.stdout


def test_review_ci_gate_passes(tmp_path: Path):
    clean = tmp_path / "ok.py"
    clean.write_text("def ok():\n    pass\n", encoding="utf-8")
    result = run_cli(
        "review",
        "--files",
        str(clean),
        "--cwd",
        str(tmp_path),
        "--ci",
        "--max-critical",
        "0",
    )
    assert result.returncode == 0


def test_review_sarif_format(tmp_path: Path):
    bad = _write_sample(tmp_path)
    result = run_cli("review", "--files", str(bad), "--cwd", str(tmp_path), "--format", "sarif")
    assert result.returncode == 0
    sarif = json.loads(result.stdout)
    assert sarif["version"] == "2.1.0"
    assert sarif["runs"][0]["results"]


def test_rules_list():
    result = run_cli("rules", "--list")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data["rules"]) >= 50


def test_rules_list_category():
    result = run_cli("rules", "--list", "--category", "security")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["rules"]
    assert all(r["category"] == "security" for r in data["rules"])


def test_rules_unknown_category():
    result = run_cli("rules", "--list", "--category", "nope")
    assert result.returncode == 1


def test_rules_add_yaml(tmp_path: Path):
    rule_file = tmp_path / "custom.yaml"
    rule_file.write_text(
        "rules:\n"
        "  - id: custom-foo-bar\n"
        "    category: security\n"
        "    severity: HIGH\n"
        "    message: foo bar detected\n"
        "    fix: avoid foo bar\n"
        "    pattern: foo_bar\n"
        "    languages: [python]\n",
        encoding="utf-8",
    )
    state = tmp_path / "state"
    env = {"CODE_REVIEWER_STATE_DIR": str(state)}
    result = run_cli("rules", "--add", str(rule_file), env=env)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert [r["id"] for r in data["added"]] == ["custom-foo-bar"]
    again = run_cli("rules", "--add", str(rule_file), env=env)
    assert "No new rules added" in again.stdout


def test_rules_add_missing_file():
    result = run_cli("rules", "--add", "does-not-exist.yaml")
    assert result.returncode == 1


def test_show_rule():
    result = run_cli("show", "security-sql-injection")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["id"] == "security-sql-injection"
    assert data["severity"] == "CRITICAL"


def test_show_unknown_rule():
    result = run_cli("show", "nope-nope")
    assert result.returncode == 1


def test_history(tmp_path: Path):
    bad = _write_sample(tmp_path)
    state = tmp_path / "state"
    env = {"CODE_REVIEWER_STATE_DIR": str(state)}
    run_cli("review", "--files", str(bad), "--cwd", str(tmp_path), env=env)
    result = run_cli("history", env=env)
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["reviews"]
    assert data["reviews"][-1]["total_findings"] >= 2


def test_history_limit():
    result = run_cli("history", "--limit", "0")
    assert result.returncode == 0


def test_no_command_fails():
    result = run_cli()
    assert result.returncode == 2
