"""Tests for rap-writer CLI."""
from unittest.mock import patch


def test_analyze_outputs_json():
    from scripts.cli import cmd_analyze

    class Args:
        lyrics = "Test lyrics here"
        output = ""

    result = cmd_analyze(Args())
    assert result == 0


def test_analyze_with_file_input(tmp_path):
    from scripts.cli import cmd_analyze

    lyrics_file = tmp_path / "lyrics.txt"
    lyrics_file.write_text("Original lyrics content")

    class Args:
        lyrics = str(lyrics_file)
        output = ""

    result = cmd_analyze(Args())
    assert result == 0


def test_adapt_outputs_json():
    from scripts.cli import cmd_adapt

    class Args:
        original = "Original lyrics"
        theme = "climate change"
        style = "boom-bap"
        output = ""

    result = cmd_adapt(Args())
    assert result == 0


def test_write_outputs_json():
    from scripts.cli import cmd_write

    class Args:
        theme = "startup life"
        structure = "verse-chorus"
        style = "trap"
        bars = 16

    result = cmd_write(Args())
    assert result == 0


def test_validate_outputs_json():
    from scripts.cli import cmd_validate

    class Args:
        original = "Original lyrics"
        adapted = "Adapted lyrics"
        strict = False

    result = cmd_validate(Args())
    assert result == 0


def test_batch_outputs_json():
    from scripts.cli import cmd_batch

    class Args:
        theme = "daily struggles"
        styles = "boom-bap,trap"
        count = 3

    result = cmd_batch(Args())
    assert result == 0


def test_export_outputs_json():
    from scripts.cli import cmd_export

    class Args:
        lyrics = "Test lyrics"
        format = "text"
        bpm = 90

    result = cmd_export(Args())
    assert result == 0


def test_analyze_with_output_file(tmp_path):
    from scripts.cli import cmd_analyze

    lyrics_file = tmp_path / "input.txt"
    lyrics_file.write_text("Test lyrics")

    output_file = tmp_path / "output.json"

    class Args:
        lyrics = str(lyrics_file)
        output = str(output_file)

    result = cmd_analyze(Args())
    assert result == 0


def test_adapt_with_output_file(tmp_path):
    from scripts.cli import cmd_adapt

    original_file = tmp_path / "original.txt"
    original_file.write_text("Original lyrics")

    output_file = tmp_path / "adapted.txt"

    class Args:
        original = str(original_file)
        theme = "technology"
        style = "conscious"
        output = str(output_file)

    result = cmd_adapt(Args())
    assert result == 0


def test_validate_strict_mode():
    from scripts.cli import cmd_validate

    class Args:
        original = "Original lyrics"
        adapted = "Adapted lyrics with same word count"
        strict = True

    result = cmd_validate(Args())
    assert result == 0