"""Tests for dynamic-context-pruning summarization."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.summarization import SummarySchema


def test_summary_schema_validation():
    schema = SummarySchema(
        fields=["title", "key_points", "action_items"],
        required=["title"],
        description="Test schema",
    )
    valid_summary = {"title": "Test", "key_points": ["point1"]}
    errors = schema.validate(valid_summary)
    assert len(errors) == 0


def test_summary_schema_missing_required():
    schema = SummarySchema(
        fields=["title", "key_points"],
        required=["title"],
    )
    invalid_summary = {"key_points": ["point1"]}
    errors = schema.validate(invalid_summary)
    assert len(errors) > 0


def test_summary_schema_unknown_field():
    schema = SummarySchema(
        fields=["title"],
        required=["title"],
    )
    invalid_summary = {"title": "Test", "extra_field": "value"}
    errors = schema.validate(invalid_summary)
    assert len(errors) > 0