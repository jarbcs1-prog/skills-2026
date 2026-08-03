"""Tests for dynamic-context-pruning compaction."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.compaction import Compactor, CompactionStrategy


def test_compactor_initializes():
    from scripts.compaction import CompactionConfig, CompactionStrategy
    config = CompactionConfig(strategy=CompactionStrategy.HYBRID)
    compactor = Compactor(config)
    assert compactor.config.strategy == CompactionStrategy.HYBRID


def test_compactor_custom_strategy():
    from scripts.compaction import CompactionConfig, CompactionStrategy
    config = CompactionConfig(strategy=CompactionStrategy.TOKEN_BUDGET)
    compactor = Compactor(config)
    assert compactor.config.strategy == CompactionStrategy.TOKEN_BUDGET


def test_compactor_compact_returns_result():
    from scripts.compaction import CompactionConfig, CompactionStrategy
    config = CompactionConfig(strategy=CompactionStrategy.HYBRID)
    compactor = Compactor(config)
    context = []
    result = compactor.compact(context)
    assert result is not None


def test_compactor_restore():
    from scripts.compaction import CompactionConfig, CompactionStrategy
    config = CompactionConfig(strategy=CompactionStrategy.HYBRID)
    compactor = Compactor(config)
    assert hasattr(compactor, 'restore')


def test_compaction_strategies_exist():
    strategies = [s.value for s in CompactionStrategy]
    assert "token_budget" in strategies
    assert "age_based" in strategies
    assert "importance_based" in strategies
    assert "hybrid" in strategies