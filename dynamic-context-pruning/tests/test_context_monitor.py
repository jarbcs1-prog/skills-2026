"""Tests for dynamic-context-pruning context monitor."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.context_monitor import ContextMonitor, ContextThresholds


def test_monitor_initializes():
    config = ContextThresholds()
    monitor = ContextMonitor(config)
    assert monitor.thresholds is not None


def test_monitor_get_metrics():
    config = ContextThresholds()
    monitor = ContextMonitor(config)
    metrics = monitor.get_metrics()
    assert metrics.tokens_used >= 0
    assert metrics.percent >= 0.0