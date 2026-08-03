#!/usr/bin/env python3
"""End-to-end tests for the writing-skills CLI.

Each test runs the CLI as a subprocess from the skill root, mirroring how a
user would invoke it. Scenarios are created in temporary directories.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "scripts.cli", *args],
        capture_output=True,
        text=True,
        cwd=str(cwd or ROOT),
    )


def make_skill(tmp_path: Path, name: str = "test-skill", template: str = "discipline") -> Path:
    result = run_cli("init", "--name", name, "--template", template, "--output", str(tmp_path))
    assert result.returncode == 0, result.stderr
    return tmp_path / name


def test_init_creates_skill(tmp_path: Path) -> None:
    skill = make_skill(tmp_path)
    assert (skill / "SKILL.md").exists()
    assert (skill / "skill.yaml").exists()
    assert (skill / "evals" / "evals.json").exists()
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert "name: test-skill" in text
    assert "description: " in text


def test_init_invalid_name_fails(tmp_path: Path) -> None:
    result = run_cli("init", "--name", "Bad Name!", "--template", "discipline", "--output", str(tmp_path))
    assert result.returncode != 0
    assert "kebab-case" in result.stdout + result.stderr


def test_init_unknown_template_fails(tmp_path: Path) -> None:
    result = run_cli("init", "--name", "ok-skill", "--template", "nope", "--output", str(tmp_path))
    assert result.returncode != 0
    assert "nope" in result.stderr


def test_init_duplicate_dir_fails(tmp_path: Path) -> None:
    make_skill(tmp_path, "dup-skill")
    result = run_cli("init", "--name", "dup-skill", "--template", "technique", "--output", str(tmp_path))
    assert result.returncode != 0
    assert "already exists" in result.stdout + result.stderr


def test_validate_passes_scaffolded(tmp_path: Path) -> None:
    skill = make_skill(tmp_path, "valid-skill", "reference")
    result = run_cli("validate", "--skill", str(skill))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "VALID" in result.stdout


def test_validate_missing_skill_fails(tmp_path: Path) -> None:
    missing = tmp_path / "nope"
    missing.mkdir()
    result = run_cli("validate", "--skill", str(missing))
    assert result.returncode != 0
    assert "SKILL.md missing" in result.stdout


def test_test_red_only(tmp_path: Path) -> None:
    skill = make_skill(tmp_path, "red-skill", "discipline")
    result = run_cli("test", "--skill", str(skill), "--red-only")
    assert result.returncode == 0
    assert "Baseline (RED)" in result.stdout
    assert "Compliance rate: 0%" in result.stdout


def test_test_green_pass_for_discipline(tmp_path: Path) -> None:
    skill = make_skill(tmp_path, "green-skill", "discipline")
    (skill / "SKILL.md").write_text(
        (skill / "SKILL.md").read_text(encoding="utf-8")
        + "\nNo exceptions. Delete code written without a failing test first. "
        "Ignore authority, exhaustion and sunk cost. Start over.\n",
        encoding="utf-8",
    )
    result = run_cli("test", "--skill", str(skill), "--green-only")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Compliance rate: 100%" in result.stdout


def test_test_full_cycle(tmp_path: Path) -> None:
    skill = make_skill(tmp_path, "cycle-skill", "technique")
    result = run_cli("test", "--skill", str(skill), "--full-cycle")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "TEST REPORT" in result.stdout
    assert "VERDICT:" in result.stdout


def test_publish_install_roundtrip(tmp_path: Path) -> None:
    registry = tmp_path / "registry"
    skill = make_skill(tmp_path, "pub-skill", "technique")
    pub = run_cli("publish", "--skill", str(skill), "--registry", str(registry))
    assert pub.returncode == 0, pub.stdout + pub.stderr
    assert "published" in pub.stdout

    target = tmp_path / "installed"
    inst = run_cli("install", "pub-skill@1.0.0", "--registry", str(registry), "--target", str(target))
    assert inst.returncode == 0, inst.stdout + inst.stderr
    assert (target / "pub-skill" / "SKILL.md").exists()


def test_install_latest_and_missing(tmp_path: Path) -> None:
    registry = tmp_path / "registry"
    skill = make_skill(tmp_path, "latest-skill", "pattern")
    run_cli("publish", "--skill", str(skill), "--registry", str(registry))
    target = tmp_path / "installed"
    result = run_cli("install", "latest-skill", "--registry", str(registry), "--target", str(target))
    assert result.returncode == 0
    assert (target / "latest-skill" / "SKILL.md").exists()

    missing = run_cli("install", "ghost", "--registry", str(registry), "--target", str(target))
    assert missing.returncode != 0
    assert "not found" in missing.stdout


def test_publish_duplicate_version_rejected(tmp_path: Path) -> None:
    registry = tmp_path / "registry"
    skill = make_skill(tmp_path, "dup-pub", "workflow")
    first = run_cli("publish", "--skill", str(skill), "--registry", str(registry))
    assert first.returncode == 0
    second = run_cli("publish", "--skill", str(skill), "--registry", str(registry))
    assert second.returncode != 0
    assert "already published" in second.stdout + second.stderr


def test_upgrade_to_higher_version(tmp_path: Path) -> None:
    registry = tmp_path / "registry"
    skill = make_skill(tmp_path, "up-skill", "monitor")
    run_cli("publish", "--skill", str(skill), "--registry", str(registry))
    run_cli("publish", "--skill", str(skill), "--version", "2.0.0", "--registry", str(registry))
    target = tmp_path / "installed"
    run_cli("install", "up-skill@1.0.0", "--registry", str(registry), "--target", str(target))

    result = run_cli("upgrade", "up-skill", "--version", "2.0.0", "--registry", str(registry), "--target", str(target))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "installed" in result.stdout

    downgrade = run_cli("upgrade", "up-skill", "--version", "1.0.0", "--registry", str(registry), "--target", str(target))
    assert downgrade.returncode != 0
    assert "downgrade" in downgrade.stdout


def test_health_report(tmp_path: Path) -> None:
    skill = make_skill(tmp_path, "health-skill", "reference")
    result = run_cli("health", "--skill", str(skill), "--period", "30d")
    assert result.returncode == 0
    assert "Skill:" in result.stdout
    assert "Coverage:" in result.stdout


def test_compose_workflow(tmp_path: Path) -> None:
    a = make_skill(tmp_path, "compose-a", "technique")
    b = make_skill(tmp_path, "compose-b", "discipline")
    result = run_cli(
        "compose", "--skills", f"{a},{b}", "--name", "my-workflow", "--output", str(tmp_path)
    )
    assert result.returncode == 0, result.stdout + result.stderr
    workflow = tmp_path / "my-workflow"
    assert (workflow / "SKILL.md").exists()
    text = (workflow / "SKILL.md").read_text(encoding="utf-8")
    assert "compose-a" in text and "compose-b" in text


def test_no_command_fails() -> None:
    result = run_cli()
    assert result.returncode != 0
