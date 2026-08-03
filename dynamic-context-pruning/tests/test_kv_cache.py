"""Tests for dynamic-context-pruning KV-cache optimizer."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.kv_cache import KVCacheOptimizer, CacheIssueType


def test_kv_cache_optimizer_initializes():
    optimizer = KVCacheOptimizer()
    assert optimizer is not None


def test_kv_cache_validate_empty_context():
    optimizer = KVCacheOptimizer()
    issues = optimizer.validate([])
    assert isinstance(issues, list)


def test_kv_cache_issue_types_exist():
    issue_types = [t.value for t in CacheIssueType]
    assert "non_deterministic_json" in issue_types
    assert "timestamps_in_prefix" in issue_types
    assert "modified_previous_messages" in issue_types