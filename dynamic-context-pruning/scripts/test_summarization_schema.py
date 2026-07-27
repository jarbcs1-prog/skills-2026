"""Tests schema validation against malformed summaries.

Ensures that the Summarizer rejects invalid structured summaries
and accepts well-formed ones, catching missing fields, wrong types,
and extra/unexpected keys.
"""

import os
import sys
import pytest
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(__file__))
from summarization import SummarySchema, Summarizer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def default_schema():
    """Standard agent summary schema with two required fields."""
    return SummarySchema(
        fields=[
            "files_modified",
            "user_goals",
            "current_state",
            "pending_actions",
            "errors_encountered",
            "key_decisions",
        ],
        required=["user_goals", "current_state"],
    )


@pytest.fixture
def minimal_schema():
    """Schema with a single required field."""
    return SummarySchema(
        fields=["status"],
        required=["status"],
    )


@pytest.fixture
def summarizer(default_schema):
    """Summarizer backed by the default schema."""
    return Summarizer(
        schema=default_schema,
        keep_recent_full=3,
        model="opencode/big-pickle",
    )


@pytest.fixture
def sample_context():
    """Minimal context history for summarization."""
    return [
        {"role": "user", "content": "Refactor the auth module"},
        {"role": "assistant", "tool": "edit", "output": "Edited auth.py"},
        {"role": "user", "content": "Now add tests"},
        {"role": "assistant", "tool": "write", "output": "Created test_auth.py"},
        {"role": "user", "content": "Run the tests"},
        {"role": "assistant", "tool": "bash", "output": "All 12 tests passed"},
    ]


# ---------------------------------------------------------------------------
# Valid summaries
# ---------------------------------------------------------------------------

class TestValidSummaries:
    """Well-formed summaries should pass validation."""

    def test_full_valid_summary(self, summarizer, sample_context):
        """A complete summary with all required fields should validate."""
        summary = {
            "files_modified": ["auth.py", "test_auth.py"],
            "user_goals": "Refactor auth module and add tests",
            "current_state": "All tests passing",
            "pending_actions": [],
            "errors_encountered": [],
            "key_decisions": ["Used pytest for test framework"],
        }
        assert summarizer.validate(summary, sample_context) is True

    def test_valid_summary_extra_fields(self, summarizer, sample_context):
        """Extra fields beyond the schema should not cause validation failure."""
        summary = {
            "files_modified": ["auth.py"],
            "user_goals": "Refactor auth",
            "current_state": "Tests green",
            "pending_actions": [],
            "errors_encountered": [],
            "key_decisions": [],
            "unexpected_field": "should not matter",
        }
        assert summarizer.validate(summary, sample_context) is True

    def test_valid_summary_minimal_required_only(self, summarizer, sample_context):
        """A summary containing only required fields (plus empty optionals) should pass."""
        summary = {
            "files_modified": [],
            "user_goals": "Do the thing",
            "current_state": "In progress",
            "pending_actions": [],
            "errors_encountered": [],
            "key_decisions": [],
        }
        assert summarizer.validate(summary, sample_context) is True


# ---------------------------------------------------------------------------
# Missing required fields
# ---------------------------------------------------------------------------

class TestMissingRequiredFields:
    """Missing required fields must cause validation failure."""

    @pytest.mark.parametrize(
        "missing_field",
        [
            "user_goals",
            "current_state",
        ],
        ids=["missing-user_goals", "missing-current_state"],
    )
    def test_single_missing_required(self, summarizer, sample_context, missing_field):
        """Omitting one required field should fail validation."""
        summary = {
            "files_modified": [],
            "user_goals": "Refactor",
            "current_state": "Done",
            "pending_actions": [],
            "errors_encountered": [],
            "key_decisions": [],
        }
        del summary[missing_field]
        assert summarizer.validate(summary, sample_context) is False

    def test_all_required_missing(self, summarizer, sample_context):
        """An empty summary should fail validation."""
        assert summarizer.validate({}, sample_context) is False


# ---------------------------------------------------------------------------
# Empty / falsy required fields
# ---------------------------------------------------------------------------

class TestFalsyRequiredFields:
    """Required fields that exist but are empty/falsy should fail."""

    @pytest.mark.parametrize(
        "summary",
        [
            {"user_goals": "", "current_state": "Active"},
            {"user_goals": "Goal", "current_state": ""},
            {"user_goals": None, "current_state": "Active"},
            {"user_goals": "Goal", "current_state": None},
            {"user_goals": [], "current_state": "Active"},
            {"user_goals": "Goal", "current_state": []},
        ],
        ids=[
            "empty-string-goals",
            "empty-string-state",
            "none-goals",
            "none-state",
            "list-goals",
            "list-state",
        ],
    )
    def test_falsy_required_values(self, summarizer, sample_context, summary):
        """Falsy values (empty string, None, empty list) in required fields should fail."""
        full_summary = {
            "files_modified": [],
            "pending_actions": [],
            "errors_encountered": [],
            "key_decisions": [],
        }
        full_summary.update(summary)
        assert summarizer.validate(full_summary, sample_context) is False


# ---------------------------------------------------------------------------
# Type checking on summary fields
# ---------------------------------------------------------------------------

class TestFieldTypeChecking:
    """Summary fields should accept the expected types."""

    def test_list_fields_accept_lists(self, summarizer, sample_context):
        """Fields like files_modified should accept lists."""
        summary = {
            "files_modified": ["a.py", "b.py"],
            "user_goals": "Refactor",
            "current_state": "Done",
            "pending_actions": ["review"],
            "errors_encountered": ["timeout"],
            "key_decisions": ["used caching"],
        }
        assert summarizer.validate(summary, sample_context) is True

    def test_string_fields_accept_strings(self, summarizer, sample_context):
        """Required text fields should accept plain strings."""
        summary = {
            "files_modified": [],
            "user_goals": "Make it faster",
            "current_state": "Benchmarking",
            "pending_actions": [],
            "errors_encountered": [],
            "key_decisions": [],
        }
        assert summarizer.validate(summary, sample_context) is True


# ---------------------------------------------------------------------------
# Summarizer output shape
# ---------------------------------------------------------------------------

class TestSummarizerOutput:
    """The summarize() method should produce output matching the schema."""

    def test_output_contains_all_fields(self, summarizer, sample_context):
        """Generated summary must include every field in the schema."""
        summary = summarizer.summarize(sample_context)
        for field in summarizer.schema.fields:
            assert field in summary, f"Missing schema field: {field}"

    def test_output_validates_against_own_schema(self, summarizer, sample_context):
        """Self-generated summaries should always pass validation."""
        summary = summarizer.summarize(sample_context)
        assert summarizer.validate(summary, sample_context) is True

    def test_minimal_schema_output(self, minimal_schema):
        """A single-field schema should produce exactly that field."""
        s = Summarizer(schema=minimal_schema, keep_recent_full=2, model="test")
        summary = s.summarize([{"role": "user", "content": "hi"}])
        assert "status" in summary
        assert len(summary) == 1


# ---------------------------------------------------------------------------
# Minimal-schema edge cases
# ---------------------------------------------------------------------------

class TestMinimalSchemaEdgeCases:
    """Edge cases with very small schemas."""

    def test_minimal_valid(self, minimal_schema):
        """Minimal schema with required field present should pass."""
        s = Summarizer(schema=minimal_schema, keep_recent_full=1, model="test")
        assert s.validate({"status": "ok"}, []) is True

    def test_minimal_missing_required(self, minimal_schema):
        """Minimal schema missing its only required field should fail."""
        s = Summarizer(schema=minimal_schema, keep_recent_full=1, model="test")
        assert s.validate({"status": ""}, []) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
