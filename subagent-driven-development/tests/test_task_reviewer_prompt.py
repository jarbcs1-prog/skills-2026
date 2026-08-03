"""Tests for task reviewer prompt template."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.task_reviewer_prompt import TASK_REVIEWER_PROMPT, get_task_reviewer_prompt


def test_task_reviewer_prompt_has_required_sections():
    assert "Task Reviewer Subagent Prompt" in TASK_REVIEWER_PROMPT
    assert "Role" in TASK_REVIEWER_PROMPT
    assert "Inputs" in TASK_REVIEWER_PROMPT
    assert "Review Criteria" in TASK_REVIEWER_PROMPT


def test_task_reviewer_prompt_has_spec_compliance():
    assert "Spec Compliance" in TASK_REVIEWER_PROMPT
    assert "All requirements from brief met" in TASK_REVIEWER_PROMPT
    assert "No extra functionality" in TASK_REVIEWER_PROMPT


def test_task_reviewer_prompt_has_code_quality():
    assert "Code Quality" in TASK_REVIEWER_PROMPT
    assert "Tests cover new code" in TASK_REVIEWER_PROMPT
    assert "No magic numbers" in TASK_REVIEWER_PROMPT


def test_task_reviewer_prompt_has_output_format():
    assert "SPEC" in TASK_REVIEWER_PROMPT
    assert "APPROVED" in TASK_REVIEWER_PROMPT
    assert "NEEDS_FIXES" in TASK_REVIEWER_PROMPT


def test_get_task_reviewer_prompt_substitutes_placeholders():
    prompt = get_task_reviewer_prompt(
        brief_path="brief.md",
        report_path="report.md",
        package_path="package.md",
        constraints_path="constraints.md",
        review_path="review.md",
    )
    assert "brief.md" in prompt
    assert "report.md" in prompt
    assert "package.md" in prompt
    assert "constraints.md" in prompt
    assert "review.md" in prompt