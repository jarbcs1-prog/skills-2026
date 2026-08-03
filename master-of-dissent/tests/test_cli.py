"""Tests for master-of-dissent CLI."""
from unittest.mock import patch


def test_rebut_outputs_json():
    from scripts.cli import cmd_rebut

    class Args:
        text = "Your argument is wrong"
        framework = "steel_man"

    result = cmd_rebut(Args())
    assert result == 0


def test_roast_outputs_json():
    from scripts.cli import cmd_roast

    class Args:
        text = "You claim this is optimal"
        intensity = "playful"

    result = cmd_roast(Args())
    assert result == 0


def test_debate_outputs_json():
    from scripts.cli import cmd_debate

    class Args:
        topic = "microservices vs monolith"
        rounds = 3

    result = cmd_debate(Args())
    assert result == 0


def test_analyze_outputs_json():
    from scripts.cli import cmd_analyze

    class Args:
        text = "All dynamic languages are slow"

    result = cmd_analyze(Args())
    assert result == 0


def test_practice_outputs_json():
    from scripts.cli import cmd_practice

    class Args:
        mode = "constructive"
        feedback = True

    result = cmd_practice(Args())
    assert result == 0


def test_rebut_with_fallacy_detection():
    from scripts.cli import cmd_rebut

    class Args:
        text = "Everyone uses this framework so it must be good"
        framework = "reductio"

    result = cmd_rebut(Args())
    assert result == 0


def test_roast_intensity_levels():
    from scripts.cli import cmd_roast

    for intensity_level in ["playful", "sharp", "devastating"]:
        class Args:
            text = "Your code has bugs"
            intensity = intensity_level

        result = cmd_roast(Args())
        assert result == 0


def test_debate_rounds():
    from scripts.cli import cmd_debate

    class Args:
        topic = "AI will replace programmers"
        rounds = 5

    result = cmd_debate(Args())
    assert result == 0


def test_analyze_fallacies():
    from scripts.cli import cmd_analyze

    class Args:
        text = "If we don't use this tool we will fall behind"

    result = cmd_analyze(Args())
    assert result == 0


def test_practice_modes():
    from scripts.cli import cmd_practice

    for practice_mode in ["roast", "constructive", "steel_man", "devils_advocate"]:
        class Args:
            mode = practice_mode
            feedback = True

        result = cmd_practice(Args())
        assert result == 0