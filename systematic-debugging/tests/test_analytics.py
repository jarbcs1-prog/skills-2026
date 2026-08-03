"""Tests for systematic-debugging analytics."""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.analytics import DebugSession, DebuggingAnalytics


def test_record_session():
    analytics = DebuggingAnalytics()
    session = DebugSession(
        id="test-1",
        start_time=datetime.now(),
        error_category="null_pointer",
        hypotheses_tested=2,
        fixes_attempted=1,
        first_fix_success=True,
        pattern_matched="null_pointer",
        time_to_root_cause_minutes=10.5,
    )
    analytics.record_session(session)
    assert len(analytics.sessions) == 1


def test_effectiveness_report():
    analytics = DebuggingAnalytics()
    for i in range(5):
        analytics.record_session(DebugSession(
            id=f"test-{i}",
            start_time=datetime.now(),
            error_category="null_pointer",
            hypotheses_tested=2,
            fixes_attempted=1,
            first_fix_success=i < 4,
            pattern_matched="null_pointer",
            time_to_root_cause_minutes=10.0 + i,
        ))
    report = analytics.get_effectiveness()
    assert report.total_sessions == 5
    assert report.first_fix_success_rate == 0.8
    assert report.avg_time_to_root_cause > 0


def test_empty_analytics():
    analytics = DebuggingAnalytics()
    report = analytics.get_effectiveness()
    assert report.total_sessions == 0
    assert report.first_fix_success_rate == 0.0


def test_pattern_effectiveness():
    analytics = DebuggingAnalytics()
    for i in range(3):
        analytics.record_session(DebugSession(
            id=f"test-{i}",
            start_time=datetime.now(),
            error_category="null_pointer",
            hypotheses_tested=2,
            fixes_attempted=1,
            first_fix_success=True,
            pattern_matched="null_pointer",
            time_to_root_cause_minutes=5.0,
        ))
    for i in range(2):
        analytics.record_session(DebugSession(
            id=f"other-{i}",
            start_time=datetime.now(),
            error_category="off_by_one",
            hypotheses_tested=3,
            fixes_attempted=2,
            first_fix_success=False,
            pattern_matched="off_by_one",
            time_to_root_cause_minutes=15.0,
        ))
    patterns = analytics.get_pattern_effectiveness()
    assert "null_pointer" in patterns
    assert "off_by_one" in patterns
    assert patterns["null_pointer"].occurrence_count == 3
    assert patterns["off_by_one"].occurrence_count == 2