"""Tests for verification-before-completion CLI."""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "scripts.cli", *args],
        capture_output=True, text=True,
        cwd=str(ROOT),
    )


def test_tests_command_pass():
    result = run_cli("tests", "--command", f'{sys.executable} -c "print(\'ok\')"', "--expect", "pass")
    assert result.returncode == 0, result.stderr


def test_tests_command_fail():
    result = run_cli("tests", "--command", f'{sys.executable} -c "raise SystemExit(1)"', "--expect", "fail")
    assert result.returncode == 0, result.stderr


def test_build_command():
    result = run_cli("build", "--command", f'{sys.executable} -c "print(\'built\')"')
    assert result.returncode == 0, result.stderr


def test_linter_command():
    result = run_cli("linter", "--command", f'{sys.executable} -c "print(\'clean\')"')
    assert result.returncode == 0, result.stderr


def test_requirements_command():
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write("- [x] tests pass\n- [x] build passes\n")
        checklist = fh.name
    try:
        result = run_cli("requirements", "--checklist", checklist, "--all")
        assert result.returncode == 0, result.stderr
    finally:
        Path(checklist).unlink(missing_ok=True)


def test_requirements_gate_blocks_unchecked():
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write("- [x] tests pass\n- [ ] build passes\n")
        checklist = fh.name
    try:
        result = run_cli("requirements", "--checklist", checklist, "--all")
        assert result.returncode == 1
    finally:
        Path(checklist).unlink(missing_ok=True)


def test_agent_command():
    result = run_cli("agent", "--task", "add feature", "--claimed-files", "scripts/cli.py", "--project", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_all_command():
    result = run_cli("all", "--project", str(ROOT), "--type", "generic", "--phase", "pre-commit")
    assert result.returncode == 0, result.stderr


def test_all_command_gate_fails_on_bad_step():
    result = run_cli(
        "all", "--project", str(ROOT), "--type", "generic", "--phase", "pre-commit", "--gate",
        "--history", str(Path(tempfile.gettempdir()) / "verify-test-history.jsonl"),
    )
    assert result.returncode == 1


def test_history_command():
    result = run_cli("history", "--period", "30d", "--stats", "--history", str(Path(tempfile.gettempdir()) / "verify-test-empty.jsonl"))
    assert result.returncode == 0, result.stderr


def test_coach_command():
    result = run_cli("coach", "--mode", "strict")
    assert result.returncode == 0, result.stderr


def test_all_command_with_override():
    history_file = str(Path(tempfile.gettempdir()) / "verify-test-override.jsonl")
    result = run_cli(
        "all", "--project", str(ROOT), "--type", "generic", "--phase", "pre-commit",
        "--override", "Emergency deploy needed for security patch",
        "--history", history_file,
    )
    assert result.returncode == 0, result.stderr
    assert "OVERRIDE" in result.stdout
    Path(history_file).unlink(missing_ok=True)


def test_no_command_shows_help():
    result = run_cli()
    assert result.returncode != 0
    assert "usage" in result.stderr or "usage" in result.stdout
