"""Tests for implementer prompt template."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.implementer_prompt import IMPLEMENTER_PROMPT, get_implementer_prompt


def test_implementer_prompt_has_required_sections():
    assert "Implementer Subagent Prompt" in IMPLEMENTER_PROMPT
    assert "Role" in IMPLEMENTER_PROMPT
    assert "Inputs" in IMPLEMENTER_PROMPT
    assert "Process" in IMPLEMENTER_PROMPT
    assert "Constraints" in IMPLEMENTER_PROMPT


def test_implementer_prompt_has_tdd_reference():
    assert "TDD" in IMPLEMENTER_PROMPT
    assert "RED" in IMPLEMENTER_PROMPT
    assert "GREEN" in IMPLEMENTER_PROMPT


def test_implementer_prompt_has_status_values():
    assert "DONE" in IMPLEMENTER_PROMPT
    assert "DONE_WITH_CONCERNS" in IMPLEMENTER_PROMPT
    assert "NEEDS_CONTEXT" in IMPLEMENTER_PROMPT
    assert "BLOCKED" in IMPLEMENTER_PROMPT


def test_get_implementer_prompt_substitutes_placeholders():
    prompt = get_implementer_prompt(
        brief_path="brief.md",
        constraints_path="constraints.md",
        interfaces_path="interfaces.md",
        report_path="report.md",
    )
    assert "brief.md" in prompt
    assert "constraints.md" in prompt
    assert "interfaces.md" in prompt
    assert "report.md" in prompt


def test_implementer_prompt_has_all_steps():
    steps = ["Read brief", "Ask questions", "Write failing test",
             "Implement minimal", "Run tests", "Self-review",
             "Commit", "Write report"]
    for step in steps:
        assert step in IMPLEMENTER_PROMPT