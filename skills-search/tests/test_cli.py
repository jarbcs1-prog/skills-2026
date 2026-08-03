"""End-to-end tests for the skills-search CLI.

Each test runs the CLI as a subprocess from the skill root against a temp fake
registry, mirroring how a user would invoke it.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "scripts.cli", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(ROOT),
    )


def write_skill(
    root: Path,
    name: str,
    description: str,
    version: str = "1.0.0",
    dependencies: str = "",
    has_tests: bool = True,
) -> None:
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    lines = ["---", f"name: {name}", f"description: {description}", f"version: {version}"]
    if dependencies:
        lines.append(f"dependencies: {dependencies}")
    lines.extend(["---", "", f"# {name}", "", "## Workflow", "", "1. Step one", "2. Step two"])
    (skill_dir / "SKILL.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if has_tests:
        (skill_dir / "tests").mkdir()


@pytest.fixture
def registry(tmp_path: Path) -> Path:
    write_skill(tmp_path, "good-skill", "A good skill for testing", dependencies="partial-skill")
    write_skill(tmp_path, "partial-skill", "A partial skill without tests", has_tests=False)
    return tmp_path


def test_find_good(registry: Path) -> None:
    result = run_cli("find", "good", "--root", str(registry))
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout)
    assert data["results"]
    assert data["results"][0]["name"] == "good-skill"


def test_list(registry: Path) -> None:
    result = run_cli("list", "--root", str(registry))
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout)
    assert [skill["name"] for skill in data["skills"]] == ["good-skill", "partial-skill"]


def test_info_good_skill(registry: Path) -> None:
    result = run_cli("info", "good-skill", "--root", str(registry))
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout)
    assert data["name"] == "good-skill"
    assert data["dependencies"] == ["partial-skill"]


def test_info_missing_exits_one(registry: Path) -> None:
    result = run_cli("info", "missing", "--root", str(registry))
    assert result.returncode == 1


def test_verify_good_skill(registry: Path) -> None:
    result = run_cli("verify", "good-skill", "--root", str(registry))
    assert result.returncode == 0, result.stdout + result.stderr


def test_verify_partial_skill_exits_one(registry: Path) -> None:
    result = run_cli("verify", "partial-skill", "--root", str(registry))
    assert result.returncode == 1


def test_recommend(registry: Path) -> None:
    result = run_cli("recommend", "testing workflow", "--root", str(registry))
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout)
    assert data["recommendations"]


def test_deps(registry: Path) -> None:
    result = run_cli("deps", "good-skill", "--root", str(registry))
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout)
    assert data["dependencies"] == ["partial-skill"]
    assert data["missing"] == []


def test_sync(registry: Path) -> None:
    result = run_cli("sync", "--root", str(registry))
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout)
    assert data["indexed"] == 2


def test_update(registry: Path) -> None:
    result = run_cli("update", "--root", str(registry))
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout)
    assert data["updated"] is True
    assert data["indexed"] == 2


def test_compose(registry: Path) -> None:
    result = run_cli("compose", "good-skill,partial-skill", "--root", str(registry))
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout)
    assert "composed" in data
    assert len(data["composed"]["workflow"]) == 4


def test_lock_and_unlock(registry: Path) -> None:
    locked = run_cli("lock", "--name", "good-skill", "--version", "1.0.0", "--root", str(registry))
    assert locked.returncode == 0, locked.stdout + locked.stderr
    assert json.loads(locked.stdout)["locked"] is True
    unlocked = run_cli("unlock", "--name", "good-skill", "--root", str(registry))
    assert unlocked.returncode == 0, unlocked.stdout + unlocked.stderr


def test_install_and_uninstall(registry: Path) -> None:
    destination = registry / "installed"
    installed = run_cli("install", "good-skill", "--root", str(registry), "--target", str(destination))
    assert installed.returncode == 0, installed.stdout + installed.stderr
    assert (destination / "good-skill" / "SKILL.md").exists()
    removed = run_cli("uninstall", "good-skill", "--target", str(destination))
    assert removed.returncode == 0, removed.stdout + removed.stderr
    assert not (destination / "good-skill").exists()


def test_install_missing_exits_one(registry: Path) -> None:
    result = run_cli("install", "ghost-skill", "--root", str(registry), "--target", str(registry / "installed"))
    assert result.returncode == 1


def test_uninstall_missing_exits_one(registry: Path) -> None:
    result = run_cli("uninstall", "ghost-skill", "--target", str(registry / "installed"))
    assert result.returncode == 1
