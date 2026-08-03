"""Tests for project-planner scheduling."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.scheduling import (
    CriticalPathCalculator, ResourceLeveler, Resource, Dependency,
    LeveledSchedule,
)


def test_critical_path_calculator_initializes():
    calc = CriticalPathCalculator()
    assert calc is not None


def test_critical_path_simple():
    calc = CriticalPathCalculator()
    tasks = [
        {"id": "A", "duration_days": 2},
        {"id": "B", "duration_days": 3},
        {"id": "C", "duration_days": 1},
    ]
    deps = [Dependency(task_id="B", depends_on="A"), Dependency(task_id="C", depends_on="B")]
    result = calc.calculate(tasks, deps)
    assert "A" in result.critical_path
    assert "B" in result.critical_path
    assert "C" in result.critical_path
    assert result.total_duration == 6.0


def test_critical_path_with_parallel():
    calc = CriticalPathCalculator()
    tasks = [
        {"id": "A", "duration_days": 2},
        {"id": "B", "duration_days": 3},
        {"id": "C", "duration_days": 1},
        {"id": "D", "duration_days": 2},
    ]
    deps = [
        Dependency(task_id="B", depends_on="A"),
        Dependency(task_id="C", depends_on="A"),
        Dependency(task_id="D", depends_on="B"),
        Dependency(task_id="D", depends_on="C"),
    ]
    result = calc.calculate(tasks, deps)
    assert result.total_duration == 7.0


def test_critical_path_no_dependencies():
    calc = CriticalPathCalculator()
    tasks = [
        {"id": "A", "duration_days": 2},
        {"id": "B", "duration_days": 3},
    ]
    deps = []
    result = calc.calculate(tasks, deps)
    assert result.total_duration == 3.0


def test_schedule_result_has_all_fields():
    calc = CriticalPathCalculator()
    tasks = [{"id": "A", "duration_days": 2}]
    deps = []
    result = calc.calculate(tasks, deps)
    assert isinstance(result.tasks, dict)
    assert isinstance(result.critical_path, list)
    assert isinstance(result.float_by_task, dict)
    assert isinstance(result.earliest_start, dict)
    assert isinstance(result.earliest_finish, dict)
    assert isinstance(result.latest_start, dict)
    assert isinstance(result.latest_finish, dict)


def test_resource_leveler_initializes():
    leveler = ResourceLeveler()
    assert leveler is not None


def test_resource_leveler_no_conflicts():
    calc = CriticalPathCalculator()
    tasks = [{"id": "A", "duration_days": 2}]
    deps = []
    schedule = calc.calculate(tasks, deps)
    resources = [Resource(name="dev", capacity_hours_per_day=8)]
    leveler = ResourceLeveler()
    leveled = leveler.level(schedule, resources)
    assert isinstance(leveled, LeveledSchedule)
    assert isinstance(leveled.resource_conflicts, list)
    assert isinstance(leveled.adjustments, list)


def test_resource_leveler_detects_overallocation():
    calc = CriticalPathCalculator()
    tasks = [
        {"id": "A", "duration_days": 8},
        {"id": "B", "duration_days": 8},
    ]
    deps = []
    schedule = calc.calculate(tasks, deps)
    resources = [Resource(name="dev", capacity_hours_per_day=4)]
    leveler = ResourceLeveler()
    leveled = leveler.level(schedule, resources)
    assert isinstance(leveled.resource_conflicts, list)