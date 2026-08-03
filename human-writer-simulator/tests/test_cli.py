"""Tests for human-writer-simulator CLI."""
from unittest.mock import patch


def test_detect_outputs_json():
    from scripts.cli import cmd_detect

    class Args:
        text = "This is a test sentence."
        detailed = False

    result = cmd_detect(Args())
    assert result == 0


def test_detect_detailed():
    from scripts.cli import cmd_detect

    class Args:
        text = "This is a test sentence."
        detailed = True

    result = cmd_detect(Args())
    assert result == 0


def test_analyze_outputs_json():
    from scripts.cli import cmd_analyze

    class Args:
        text = "This is a test sentence."
        style_profile = "conversational"

    result = cmd_analyze(Args())
    assert result == 0


def test_rewrite_outputs_json():
    from scripts.cli import cmd_rewrite

    class Args:
        text = "This is a test sentence."
        style = "conversational"
        imperfections = 0.3
        output = ""

    result = cmd_rewrite(Args())
    assert result == 0


def test_rewrite_with_output_file(tmp_path):
    from scripts.cli import cmd_rewrite

    output_file = tmp_path / "output.json"

    class Args:
        text = "This is a test sentence."
        style = "conversational"
        imperfections = 0.3
        output = str(output_file)

    result = cmd_rewrite(Args())
    assert result == 0
    assert output_file.exists()


def test_batch_outputs_json(tmp_path):
    from scripts.cli import cmd_batch

    in_dir = tmp_path / "input"
    out_dir = tmp_path / "output"
    in_dir.mkdir()
    (in_dir / "test1.txt").write_text("This is test sentence one.")
    (in_dir / "test2.txt").write_text("This is test sentence two.")

    class Args:
        input_dir = str(in_dir)
        output_dir = str(out_dir)
        style = "conversational"

    result = cmd_batch(Args())
    assert result == 0


def test_compare_outputs_json():
    from scripts.cli import cmd_compare

    class Args:
        original = "This is the original text."
        rewritten = "This is the rewritten text."
        blind_test = False

    result = cmd_compare(Args())
    assert result == 0


def test_calibrate_outputs_json(tmp_path):
    from scripts.cli import cmd_calibrate

    human_dir = tmp_path / "human"
    ai_dir = tmp_path / "ai"
    human_dir.mkdir()
    ai_dir.mkdir()
    (human_dir / "sample1.txt").write_text("I think this works well in practice.")
    (ai_dir / "sample1.txt").write_text("The system processes data efficiently.")

    class Args:
        human_samples = str(human_dir)
        ai_samples = str(ai_dir)

    result = cmd_calibrate(Args())
    assert result == 0
