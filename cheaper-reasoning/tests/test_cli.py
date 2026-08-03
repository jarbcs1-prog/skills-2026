"""Tests for cheaper-reasoning CLI."""
import json
from unittest.mock import patch


def test_think_outputs_json(tmp_path):
    from scripts.cli import cmd_think

    class Args:
        topic = "test topic"
        input = "Some input text for reasoning"
        mode = "deep"
        budget = 15000
        checkpoint = ""

    result = cmd_think(Args())
    assert result == 0


def test_think_with_file_input(tmp_path):
    from scripts.cli import cmd_think

    input_file = tmp_path / "input.txt"
    input_file.write_text("File-based input for reasoning")

    class Args:
        topic = "file input test"
        input = str(input_file)
        mode = "standard"
        budget = 10000
        checkpoint = ""

    result = cmd_think(Args())
    assert result == 0


def test_resume_missing_checkpoint():
    from scripts.cli import cmd_resume

    class Args:
        checkpoint = "/nonexistent/path/checkpoint.json"

    result = cmd_resume(Args())
    assert result == 1


def test_resume_valid_checkpoint(tmp_path):
    from scripts.cli import cmd_resume

    cp = tmp_path / "checkpoint.json"
    cp.write_text(json.dumps({"contemplation": "test", "history": []}))

    class Args:
        checkpoint = str(cp)

    result = cmd_resume(Args())
    assert result == 0


def test_analyze_missing_file():
    from scripts.cli import cmd_analyze

    class Args:
        input = "/nonexistent/trace.json"

    result = cmd_analyze(Args())
    assert result == 1


def test_analyze_valid_trace(tmp_path):
    from scripts.cli import cmd_analyze

    trace = tmp_path / "trace.json"
    trace.write_text(json.dumps({"contemplation": "deep thinking here", "history": ["step1", "step2"]}))

    class Args:
        input = str(trace)

    result = cmd_analyze(Args())
    assert result == 0


def test_check_no_triggers():
    from scripts.cli import cmd_check

    class Args:
        complexity = 0.3
        uncertainty = 0.2
        architecture = False
        conflicting = False
        explicit = False

    result = cmd_check(Args())
    assert result == 0


def test_check_explicit_request():
    from scripts.cli import cmd_check

    class Args:
        complexity = 0.3
        uncertainty = 0.2
        architecture = False
        conflicting = False
        explicit = True

    result = cmd_check(Args())
    assert result == 0


def test_check_architecture_decision():
    from scripts.cli import cmd_check

    class Args:
        complexity = 0.3
        uncertainty = 0.2
        architecture = True
        conflicting = False
        explicit = False

    result = cmd_check(Args())
    assert result == 0


def test_check_conflicting_constraints():
    from scripts.cli import cmd_check

    class Args:
        complexity = 0.3
        uncertainty = 0.2
        architecture = False
        conflicting = True
        explicit = False

    result = cmd_check(Args())
    assert result == 0