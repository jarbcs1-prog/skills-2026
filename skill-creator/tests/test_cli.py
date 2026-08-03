"""End-to-end CLI tests for skill-creator (subprocess-based)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_cli(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "scripts.cli", *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        timeout=120,
    )


def make_skill(tmp_path: Path, name: str = "my-tool", template: str = "tool") -> Path:
    result = run_cli("init", "--name", name, "--template", template, "--output", str(tmp_path))
    assert result.returncode == 0, result.stdout + result.stderr
    skill = tmp_path / name
    assert (skill / "SKILL.md").exists()
    return skill


def test_init_creates_skill(tmp_path: Path) -> None:
    skill = make_skill(tmp_path)
    assert (skill / "SKILL.md").exists()
    assert (skill / "skill.yaml").exists()
    assert (skill / "evals" / "evals.json").exists()
    assert (skill / ".github" / "workflows" / "skill-test.yml").exists()
    assert (skill / "scripts" / "validate_skill.py").exists()
    assert (skill / "tests" / "test_skill.py").exists()
    assert (skill / "scripts" / "__init__.py").exists()
    assert (skill / "tests" / "__init__.py").exists()
    assert (skill / "references" / "README.md").exists()
    assert (skill / "assets" / "README.md").exists()
    name = skill.joinpath("SKILL.md").read_text(encoding="utf-8").splitlines()[1]
    assert "my-tool" in name


def test_init_invalid_name_fails(tmp_path: Path) -> None:
    result = run_cli(
        "init", "--name", "Bad Name!", "--template", "tool", "--output", str(tmp_path)
    )
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "kebab-case" in combined


def test_init_unknown_template_fails(tmp_path: Path) -> None:
    result = run_cli(
        "init", "--name", "my-skill", "--template", "nope", "--output", str(tmp_path)
    )
    assert result.returncode != 0
    assert "invalid choice" in result.stderr


def test_init_duplicate_dir_fails(tmp_path: Path) -> None:
    make_skill(tmp_path)
    result = run_cli(
        "init", "--name", "my-tool", "--template", "tool", "--output", str(tmp_path)
    )
    assert result.returncode != 0
    assert "already exists" in result.stdout + result.stderr


def test_init_all_templates(tmp_path: Path) -> None:
    for template in (
        "analysis",
        "integration",
        "workflow",
        "review",
        "generator",
        "monitor",
        "transform",
        "validator",
        "router",
    ):
        result = run_cli(
            "init", "--name", f"my-{template}", "--template", template, "--output", str(tmp_path)
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert (tmp_path / f"my-{template}" / "evals" / "evals.json").exists()


def test_validate_passes_scaffolded(tmp_path: Path) -> None:
    make_skill(tmp_path)
    result = run_cli("validate", "--skill", str(tmp_path / "my-tool"))
    assert result.returncode == 0
    assert "VALID" in result.stdout


def test_validate_strict_fails_bad_description(tmp_path: Path) -> None:
    skill = make_skill(tmp_path)
    skill_md = skill / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    text = text.replace(
        "description: A focused tool for one practical task",
        "description: " + "x" * 1500,
    )
    skill_md.write_text(text, encoding="utf-8")
    result = run_cli("validate", "--skill", str(skill), "--strict")
    assert result.returncode != 0
    assert "exceeds 1024" in result.stdout


def test_validate_missing_skill_fails(tmp_path: Path) -> None:
    result = run_cli("validate", "--skill", str(tmp_path / "nope"))
    assert result.returncode != 0
    assert "INVALID" in result.stdout


def test_publish_install_roundtrip(tmp_path: Path) -> None:
    make_skill(tmp_path)
    registry = tmp_path / "registry"
    skill = tmp_path / "my-tool"
    result = run_cli("publish", "--skill", str(skill), "--registry", str(registry))
    assert result.returncode == 0
    assert "Published my-tool@1.0.0" in result.stdout

    install_dir = tmp_path / "installed"
    install_dir.mkdir()
    result = run_cli("install", "my-tool", "--registry", str(registry), "--target", str(install_dir))
    assert result.returncode == 0
    assert (install_dir / "my-tool" / "SKILL.md").exists()
    assert "Installed my-tool@1.0.0" in result.stdout


def test_publish_duplicate_version_rejected(tmp_path: Path) -> None:
    make_skill(tmp_path)
    registry = tmp_path / "registry"
    skill = tmp_path / "my-tool"
    first = run_cli("publish", "--skill", str(skill), "--registry", str(registry))
    assert first.returncode == 0
    second = run_cli("publish", "--skill", str(skill), "--registry", str(registry))
    assert second.returncode != 0
    assert "already published" in second.stdout


def test_install_missing_skill_fails(tmp_path: Path) -> None:
    registry = tmp_path / "registry"
    result = run_cli("install", "ghost", "--registry", str(registry), "--target", str(tmp_path))
    assert result.returncode != 0
    assert "not found" in result.stdout


def test_publish_invalid_version(tmp_path: Path) -> None:
    skill = make_skill(tmp_path)
    manifest = skill / "skill.yaml"
    text = manifest.read_text(encoding="utf-8")
    text = text.replace("version: 1.0.0", "version: banana")
    manifest.write_text(text, encoding="utf-8")
    result = run_cli("publish", "--skill", str(skill), "--registry", str(tmp_path / "registry"))
    assert result.returncode != 0
    assert "invalid version" in result.stdout


def test_deps_no_dependencies(tmp_path: Path) -> None:
    skill = make_skill(tmp_path)
    result = run_cli("deps", "--skill", str(skill), "--registry", str(tmp_path / "registry"))
    assert result.returncode == 0
    assert "No dependencies" in result.stdout


def test_templates_lists_all(tmp_path: Path) -> None:
    result = run_cli("templates")
    assert result.returncode == 0
    for name in (
        "tool",
        "analysis",
        "integration",
        "workflow",
        "review",
        "generator",
        "monitor",
        "transform",
        "validator",
        "router",
    ):
        assert name in result.stdout


def test_templates_describe(tmp_path: Path) -> None:
    result = run_cli("templates", "--describe")
    assert result.returncode == 0
    assert "router:" in result.stdout


def test_optimize_missing_eval_set(tmp_path: Path) -> None:
    skill = make_skill(tmp_path)
    result = run_cli(
        "optimize",
        "--skill",
        str(skill),
        "--eval-set",
        str(tmp_path / "nope.json"),
        "--model",
        "test-model",
    )
    assert result.returncode != 0
    assert "ERROR" in result.stdout


def test_optimize_missing_skill(tmp_path: Path) -> None:
    result = run_cli(
        "optimize",
        "--skill",
        str(tmp_path / "nope"),
        "--eval-set",
        str(tmp_path / "nope.json"),
        "--model",
        "test-model",
    )
    assert result.returncode != 0


def test_no_command_fails(tmp_path: Path) -> None:
    result = run_cli()
    assert result.returncode != 0
