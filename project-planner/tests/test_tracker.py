"""Tests for project-planner tracker."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.tracker import (
    TaskUpdate, TaskStatus, PlanTracker,
)


def test_tracker_logs_update():
    tracker = PlanTracker()
    update = TaskUpdate(task_id="T1", status="done", notes="Completed")
    tracker.updates.append(update)
    assert len(tracker.updates) == 1


def test_tracker_update_progress():
    tracker = PlanTracker()
    status = tracker.update_progress("T1", "done", actual_days=3.0, notes="Done")
    assert status.task_id == "T1"
    assert status.status == "done"
    assert status.actual_days == 3.0


def test_tracker_get_progress():
    tracker = PlanTracker()
    tracker.update_progress("T1", "done")
    tracker.update_progress("T2", "done")
    tracker.update_progress("T3", "in_progress")
    progress = tracker.get_progress()
    assert progress["completed"] == 2
    assert progress["in_progress"] == 1
    assert progress["not_started"] == 0
    assert progress["completion_rate"] == 2 / 3


def test_tracker_empty_progress():
    tracker = PlanTracker()
    progress = tracker.get_progress()
    assert progress["completed"] == 0
    assert progress["completion_rate"] == 0.0


def test_tracker_completed_tasks():
    tracker = PlanTracker()
    tracker.update_progress("T1", "done")
    tracker.update_progress("T2", "done")
    tracker.update_progress("T3", "in_progress")
    assert len(tracker.completed_tasks) == 2
    assert "T1" in tracker.completed_tasks
    assert "T2" in tracker.completed_tasks


def test_tracker_multiple_updates_same_task():
    tracker = PlanTracker()
    tracker.update_progress("T1", "in_progress", actual_days=2.0)
    tracker.update_progress("T1", "done", actual_days=5.0)
    assert tracker.task_statuses["T1"].status == "done"
    assert tracker.task_statuses["T1"].actual_days == 5.0


def test_burndown_generation():
    from scripts.tracker import PlanTracker, TaskStatus
    tracker = PlanTracker()
    planned = [
        TaskStatus(task_id="T1", name="T1", status="done", progress=3.0, actual_days=3.0),
        TaskStatus(task_id="T2", name="T2", status="in_progress", progress=2.0, actual_days=1.0),
        TaskStatus(task_id="T3", name="T3", status="not_started", progress=2.0, actual_days=0.0),
    ]
    burndown = tracker.generate_burndown(total_days=10, planned_tasks=planned)
    assert burndown.total_tasks == 3
    assert len(burndown.days) == 10
    assert len(burndown.ideal_remaining) == 10
    assert len(burndown.actual_remaining) == 10


def test_variance_analysis():
    from scripts.tracker import PlanTracker, TaskStatus
    tracker = PlanTracker()
    planned = [
        TaskStatus(task_id="T1", name="T1", status="done", progress=3.0, actual_days=5.0),
        TaskStatus(task_id="T2", name="T2", status="done", progress=2.0, actual_days=2.0),
        TaskStatus(task_id="T3", name="T3", status="done", progress=4.0, actual_days=3.0),
    ]
    report = tracker.variance_analysis(planned)
    assert report.total_planned_days == 9.0
    assert report.total_actual_days == 10.0
    assert report.total_variance == 1.0
    assert len(report.by_task) == 3


def test_variance_analysis_no_variance():
    tracker = PlanTracker()
    planned = [
        TaskStatus(task_id="T1", name="T1", status="done", progress=3.0, actual_days=3.0),
    ]
    report = tracker.variance_analysis(planned)
    assert report.total_variance == 0.0