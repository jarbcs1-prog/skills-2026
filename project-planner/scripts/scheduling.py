"""Critical path calculation and resource leveling for project-planner skill."""
from dataclasses import dataclass, field
from typing import List, Dict
from collections import defaultdict


@dataclass
class Dependency:
    task_id: str
    depends_on: str


@dataclass
class ScheduleResult:
    tasks: Dict[str, Dict]
    critical_path: List[str]
    total_duration: float
    float_by_task: Dict[str, float]
    earliest_start: Dict[str, float]
    earliest_finish: Dict[str, float]
    latest_start: Dict[str, float]
    latest_finish: Dict[str, float]


@dataclass
class Resource:
    name: str
    capacity_hours_per_day: float
    assigned_tasks: List[str] = field(default_factory=list)


@dataclass
class LeveledSchedule:
    schedule: ScheduleResult
    resource_conflicts: List[Dict]
    adjustments: List[Dict]


class CriticalPathCalculator:
    def calculate(self, tasks: List[Dict], dependencies: List[Dependency]) -> ScheduleResult:
        task_map = {t["id"]: t for t in tasks}
        dep_map = defaultdict(list)
        for dep in dependencies:
            dep_map[dep.task_id].append(dep.depends_on)

        earliest_start = {}
        earliest_finish = {}
        latest_start = {}
        latest_finish = {}

        sorted_tasks = self._topological_sort(tasks, dependencies)

        for task_id in sorted_tasks:
            deps = dep_map.get(task_id, [])
            if not deps:
                earliest_start[task_id] = 0
            else:
                earliest_start[task_id] = max(
                    earliest_finish[d] for d in deps
                )
            duration = task_map[task_id].get("duration_days", 1)
            earliest_finish[task_id] = earliest_start[task_id] + duration

        for task_id in reversed(sorted_tasks):
            deps = dep_map.get(task_id, [])
            dependents = [t for t in sorted_tasks if task_id in dep_map.get(t, [])]

            if not dependents:
                latest_finish[task_id] = earliest_finish[task_id]
            else:
                latest_finish[task_id] = min(
                    latest_start[d] for d in dependents
                )
            duration = task_map[task_id].get("duration_days", 1)
            latest_start[task_id] = latest_finish[task_id] - duration

        float_by_task = {}
        for task_id in sorted_tasks:
            float_by_task[task_id] = latest_start[task_id] - earliest_start[task_id]

        critical_path = [t_id for t_id in sorted_tasks if float_by_task[t_id] == 0]
        total_duration = max(earliest_finish.values()) if earliest_finish else 0

        return ScheduleResult(
            tasks={t_id: {"duration": task_map[t_id].get("duration_days", 1),
                          "early_start": earliest_start[t_id],
                          "early_finish": earliest_finish[t_id],
                          "late_start": latest_start[t_id],
                          "late_finish": latest_finish[t_id],
                          "float": float_by_task[t_id]}
                   for t_id in sorted_tasks},
            critical_path=critical_path,
            total_duration=total_duration,
            float_by_task=float_by_task,
            earliest_start=earliest_start,
            earliest_finish=earliest_finish,
            latest_start=latest_start,
            latest_finish=latest_finish,
        )

    def _topological_sort(self, tasks: List[Dict], dependencies: List[Dependency]) -> List[str]:
        task_ids = {t["id"] for t in tasks}
        dep_map = defaultdict(list)
        in_degree = {tid: 0 for tid in task_ids}

        for dep in dependencies:
            if dep.task_id in task_ids and dep.depends_on in task_ids:
                dep_map[dep.depends_on].append(dep.task_id)
                in_degree[dep.task_id] += 1

        queue = [tid for tid, deg in in_degree.items() if deg == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)
            for neighbor in dep_map[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return result


class ResourceLeveler:
    def level(self, schedule: ScheduleResult, resources: List[Resource]) -> LeveledSchedule:
        conflicts = []
        adjustments = []

        for resource in resources:
            daily_load = defaultdict(float)
            for task_id, info in schedule.tasks.items():
                task_days = info["duration"]
                start_day = int(info["early_start"])
                for day in range(start_day, start_day + int(task_days)):
                    daily_load[day] += task_days / max(task_days, 1)

            for day, load in sorted(daily_load.items()):
                if load > resource.capacity_hours_per_day:
                    conflicts.append({
                        "resource": resource.name,
                        "day": day,
                        "load": load,
                        "capacity": resource.capacity_hours_per_day,
                        "overallocation": load - resource.capacity_hours_per_day,
                    })

        if conflicts:
            for conflict in conflicts[:5]:
                adjustments.append({
                    "action": "delay_non_critical",
                    "resource": conflict["resource"],
                    "day": conflict["day"],
                    "overallocation": conflict["overallocation"],
                })

        return LeveledSchedule(
            schedule=schedule,
            resource_conflicts=conflicts,
            adjustments=adjustments,
        )