"""Subprocess tests for scripts.cli."""

from __future__ import annotations

import json
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


def _write_valid_doc(path: Path) -> None:
    sections = [
        "Purpose",
        "Scope",
        "Architecture",
        "Components",
        "Data Flow",
        "Error Handling",
        "Testing",
        "Tradeoffs Considered",
    ]
    content = "\n".join(f"## {name}\n\nplaceholder\n" for name in sections)
    path.write_text(content, encoding="utf-8")


def test_cli_validate_valid_doc(tmp_path):
    doc = tmp_path / "design.md"
    _write_valid_doc(doc)
    result = run_cli("validate", str(doc))
    assert result.returncode == 0
    assert json.loads(result.stdout)["valid"] is True


def test_cli_validate_missing_sections(tmp_path):
    doc = tmp_path / "design.md"
    doc.write_text("## Purpose\n\nplaceholder\n", encoding="utf-8")
    result = run_cli("validate", str(doc))
    assert result.returncode == 1
    assert json.loads(result.stdout)["valid"] is False


def test_cli_decide():
    result = run_cli(
        "decide",
        "--criteria",
        "cost,time,risk",
        "--weights",
        "0.4,0.3,0.3",
        "--options",
        "build,buy,partner",
    )
    assert result.returncode == 0
    assert "winner" in json.loads(result.stdout)


def test_cli_decide_weight_mismatch():
    result = run_cli(
        "decide",
        "--criteria",
        "cost,time,risk",
        "--weights",
        "0.5,0.5",
        "--options",
        "build,buy,partner",
    )
    assert result.returncode == 1
    assert "error" in json.loads(result.stdout)


def test_cli_template_design_doc():
    result = run_cli("template", "--type", "design-doc")
    assert result.returncode == 0
    assert "## Purpose" in result.stdout
    assert "## Tradeoffs Considered" in result.stdout


def test_cli_template_decisions():
    result = run_cli("template", "--type", "decisions")
    assert result.returncode == 0
    assert "## Options" in result.stdout


def test_cli_template_bogus():
    result = run_cli("template", "--type", "bogus")
    assert result.returncode == 2


def test_cli_diff(tmp_path):
    base = tmp_path / "base.md"
    target = tmp_path / "target.md"
    base.write_text("# A\n## B\n## C\n", encoding="utf-8")
    target.write_text("## B\n## C\n## D\n", encoding="utf-8")
    result = run_cli("diff", "--base", str(base), "--target", str(target))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["added_sections"] == ["D"]
    assert data["removed_sections"] == ["A"]
