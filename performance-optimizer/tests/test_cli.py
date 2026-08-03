from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

VULNERABLE = '''def build():
    out = ""
    for i in range(10):
        out = out += "x"
    return out
'''


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "scripts.cli", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(ROOT),
    )


@pytest.fixture(autouse=True)
def _cleanup_local_files() -> None:
    yield
    for name in (".perf_baseline.json", ".perf_rules.yaml"):
        path = ROOT / name
        if path.exists():
            path.unlink()


def test_analyze_finds_rule(tmp_path) -> None:
    target = tmp_path / "vuln.py"
    target.write_text(VULNERABLE, encoding="utf-8")
    result = run_cli("analyze", "--target", str(target), "--language", "python")
    assert result.returncode == 0
    assert "findings" in result.stdout
    assert "py-string-concat-loop" in result.stdout


def test_analyze_profile(tmp_path) -> None:
    target = tmp_path / "vuln.py"
    target.write_text(VULNERABLE, encoding="utf-8")
    result = run_cli("analyze", "--target", str(target), "--language", "python", "--profile")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "profile" in data
    assert "tools" in data["profile"]


def test_analyze_missing_target() -> None:
    result = run_cli("analyze", "--target", str(ROOT / "does_not_exist_xyz.py"), "--language", "python")
    assert result.returncode == 1


def test_analyze_glob(tmp_path) -> None:
    (tmp_path / "a.py").write_text(VULNERABLE, encoding="utf-8")
    (tmp_path / "b.py").write_text(VULNERABLE, encoding="utf-8")
    pattern = str(tmp_path / "*.py")
    result = run_cli("analyze", "--target", pattern, "--language", "python")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data["files"]) == 2


def test_rules_list() -> None:
    result = run_cli("rules", "--language", "python", "--list")
    assert result.returncode == 0
    assert "py-string-concat-loop" in result.stdout


def test_rules_add(tmp_path) -> None:
    yaml_file = tmp_path / "custom.yaml"
    yaml_file.write_text("rules:\n  - id: custom-rule\n    severity: MEDIUM\n    message: custom\n", encoding="utf-8")
    result = run_cli("rules", "--add", str(yaml_file))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["added"] == 1


def test_report_html(tmp_path) -> None:
    findings = [{"rule_id": "x", "severity": "HIGH", "message": "m", "fix": "f", "line": 1}]
    results = tmp_path / "results.json"
    results.write_text(json.dumps(findings), encoding="utf-8")
    output = tmp_path / "out.html"
    result = run_cli("report", "--input", str(results), "--format", "html", "--output", str(output))
    assert result.returncode == 0
    assert output.exists()
    assert "Performance Findings" in output.read_text(encoding="utf-8")


def test_report_bad_format(tmp_path) -> None:
    results = tmp_path / "results.json"
    results.write_text("[]", encoding="utf-8")
    output = tmp_path / "out.xml"
    result = run_cli("report", "--input", str(results), "--format", "xml", "--output", str(output))
    assert result.returncode == 1


def test_gate_fails_over_budget(tmp_path) -> None:
    results = tmp_path / "r.json"
    results.write_text(json.dumps({"latency": 250}), encoding="utf-8")
    result = run_cli("gate", "--budget", "latency=100ms", "--results", str(results), "--ci")
    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert data["passed"] is False
    assert data["violations"]


def test_gate_passes_within_budget(tmp_path) -> None:
    results = tmp_path / "r.json"
    results.write_text(json.dumps({"latency": 50}), encoding="utf-8")
    result = run_cli("gate", "--budget", "latency=100ms", "--results", str(results), "--ci")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["passed"] is True


def test_profile_stub() -> None:
    result = run_cli("profile", "--command", "python app.py", "--duration", "5")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["duration"] == 5
    assert data["note"]


def test_benchmark_run(tmp_path) -> None:
    suite = tmp_path / "suite.py"
    suite.write_text("import time\ndef bench():\n    time.sleep(0.001)\n", encoding="utf-8")
    result = run_cli("benchmark", "--suite", str(suite), "--iterations", "2", "--warmup", "1")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["results"]["samples"] == 2
    assert data["results"]["mean_ms"] > 0


def test_benchmark_compare_baseline_regression(tmp_path) -> None:
    suite = tmp_path / "suite.py"
    suite.write_text("import time\ndef bench():\n    time.sleep(0.001)\n", encoding="utf-8")
    stored = run_cli("benchmark", "--suite", str(suite), "--store-baseline", "--iterations", "3", "--warmup", "1")
    assert stored.returncode == 0
    suite.write_text("import time\ndef bench():\n    time.sleep(0.02)\n", encoding="utf-8")
    compared = run_cli("benchmark", "--suite", str(suite), "--compare-baseline", "--iterations", "3", "--warmup", "1")
    assert compared.returncode == 0
    data = json.loads(compared.stdout)
    assert data["compare"]["status"] == "regressed"
