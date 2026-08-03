"""Project plan tracker and progress monitoring."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict
from collections import defaultdict


@dataclass
class TaskUpdate:
    task_id: str
    status: str
    notes: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TaskStatus:
    task_id: str
    name: str
    status: str
    progress: float = 0.0
    actual_days: float = 0.0
    variance: float = 0.0


@dataclass
class BurndownData:
    days: List[int]
    ideal_remaining: List[float]
    actual_remaining: List[float]
    projected_completion_day: int
    total_tasks: int
    completed_tasks: int


@dataclass
class VarianceReport:
    total_planned_days: float
    total_actual_days: float
    total_variance: float
    by_phase: Dict[str, float]
    by_task: List[Dict[str, float]]
    root_causes: List[str]


class PlanTracker:
    def __init__(self):
        self.task_statuses: Dict[str, TaskStatus] = {}
        self.updates: List[TaskUpdate] = []
        self.completed_tasks: List[str] = []

    def update_progress(self, task_id: str, status: str,
                        actual_days: float = 0.0, notes: str = "") -> TaskStatus:
        update = TaskUpdate(task_id=task_id, status=status, notes=notes)
        self.updates.append(update)

        if task_id not in self.task_statuses:
            self.task_statuses[task_id] = TaskStatus(
                task_id=task_id, name=task_id, status=status,
                actual_days=actual_days,
            )
        else:
            ts = self.task_statuses[task_id]
            ts.status = status
            ts.actual_days = actual_days
            ts.variance = ts.actual_days - ts.progress

        if status == "done":
            self.completed_tasks.append(task_id)

        return self.task_statuses[task_id]

    def get_progress(self) -> Dict[str, float]:
        total = len(self.task_statuses)
        if total == 0:
            return {"completed": 0, "in_progress": 0, "not_started": 0, "completion_rate": 0.0}

        done = sum(1 for ts in self.task_statuses.values() if ts.status == "done")
        in_progress = sum(1 for ts in self.task_statuses.values() if ts.status == "in_progress")
        not_started = total - done - in_progress

        return {
            "completed": done,
            "in_progress": in_progress,
            "not_started": not_started,
            "completion_rate": done / total,
        }

    def generate_burndown(self, total_days: int,
                           planned_tasks: List[TaskStatus]) -> BurndownData:
        ideal_per_day = sum(t.progress for t in planned_tasks) / max(total_days, 1)
        ideal_remaining = []
        actual_remaining = []
        completed_count = 0

        for day in range(1, total_days + 1):
            ideal_remaining.append(ideal_per_day * (total_days - day))
            actual_remaining.append(max(0, ideal_per_day * (total_days - day) - completed_count))

        return BurndownData(
            days=list(range(1, total_days + 1)),
            ideal_remaining=ideal_remaining,
            actual_remaining=actual_remaining,
            projected_completion_day=total_days,
            total_tasks=len(planned_tasks),
            completed_tasks=completed_count,
        )

    def variance_analysis(self, planned_tasks: List[TaskStatus]) -> VarianceReport:
        total_planned = sum(t.progress for t in planned_tasks)
        total_actual = sum(t.actual_days for t in planned_tasks)
        total_variance = total_actual - total_planned

        by_phase = defaultdict(float)
        for t in planned_tasks:
            by_phase[t.task_id] = t.actual_days - t.progress

        by_task = []
        for t in planned_tasks:
            by_task.append({
                "task_id": t.task_id,
                "planned": t.progress,
                "actual": t.actual_days,
                "variance": t.actual_days - t.progress,
            })

        root_causes = []
        if total_variance > 0:
            root_causes.append("Tasks took longer than planned")
        if any(t.actual_days > t.progress * 1.5 for t in planned_tasks):
            root_causes.append("Some tasks significantly exceeded estimates")

        return VarianceReport(
            total_planned_days=total_planned,
            total_actual_days=total_actual,
            total_variance=total_variance,
            by_phase=dict(by_phase),
            by_task=by_task,
            root_causes=root_causes,
        )