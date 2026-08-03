"""Tests for conversation tracker."""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.tracker import ConversationLog, ConversationTracker


def test_tracker_logs_conversation():
    tracker = ConversationTracker()
    log = ConversationLog(
        id="test-1",
        type="feedback",
        person="Alex",
        date=datetime.now(),
        framework="SBI",
        outcome="resolved",
        resolution_score=0.8,
        relationship_impact=0.7,
        clarity_score=0.9,
    )
    tracker.log(log)
    assert len(tracker.entries) == 1


def test_tracker_gets_analytics():
    tracker = ConversationTracker()
    for i in range(5):
        log = ConversationLog(
            id=f"test-{i}",
            type="feedback",
            person="Alex",
            date=datetime.now(),
            framework="SBI",
            outcome="resolved" if i < 4 else "partial",
            resolution_score=0.8,
            relationship_impact=0.7,
            clarity_score=0.9,
        )
        tracker.log(log)

    analytics = tracker.get_analytics()
    assert analytics.total_conversations == 5
    assert analytics.resolution_rate == 0.8


def test_tracker_filters_by_person():
    tracker = ConversationTracker()
    tracker.log(ConversationLog(
        id="1", type="feedback", person="Alex", date=datetime.now(),
        framework="SBI", outcome="resolved", resolution_score=0.8,
        relationship_impact=0.7, clarity_score=0.9,
    ))
    tracker.log(ConversationLog(
        id="2", type="feedback", person="Jordan", date=datetime.now(),
        framework="SBI", outcome="resolved", resolution_score=0.9,
        relationship_impact=0.8, clarity_score=0.9,
    ))

    history = tracker.get_history(person="Alex")
    assert len(history) == 1
    assert history[0].person == "Alex"


def test_tracker_returns_empty_analytics():
    tracker = ConversationTracker()
    analytics = tracker.get_analytics()
    assert analytics.total_conversations == 0
    assert analytics.resolution_rate == 0.0


def test_tracker_detects_recurring_patterns():
    tracker = ConversationTracker()
    for i in range(4):
        tracker.log(ConversationLog(
            id=f"test-{i}", type="feedback", person="Alex", date=datetime.now(),
            framework="SBI", outcome="resolved", resolution_score=0.8,
            relationship_impact=0.7, clarity_score=0.9,
        ))

    analytics = tracker.get_analytics()
    assert len(analytics.recurring_patterns) > 0