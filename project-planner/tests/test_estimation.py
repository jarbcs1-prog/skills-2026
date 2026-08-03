"""Tests for project-planner estimation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.estimation import (
    TaskEstimate, MonteCarloEstimator, three_point_estimate, t_shirt_to_days,
)


def test_task_estimate_expected_value():
    est = TaskEstimate(task_id="T1", optimistic=1, likely=3, pessimistic=5)
    assert est.expected == 3.0


def test_task_estimate_variance():
    est = TaskEstimate(task_id="T1", optimistic=1, likely=3, pessimistic=5)
    assert est.variance == (4 / 6) ** 2


def test_task_estimate_std_dev():
    est = TaskEstimate(task_id="T1", optimistic=1, likely=3, pessimistic=5)
    assert est.std_dev > 0


def test_three_point_estimate():
    est = three_point_estimate(1, 3, 5)
    assert est.optimistic == 1
    assert est.likely == 3
    assert est.pessimistic == 5


def test_t_shirt_to_days_xs():
    opt, likely, pess = t_shirt_to_days("XS")
    assert opt == 0.5
    assert likely == 1
    assert pess == 2


def test_t_shirt_to_days_s():
    opt, likely, pess = t_shirt_to_days("S")
    assert opt == 1
    assert likely == 2
    assert pess == 4


def test_t_shirt_to_days_m():
    opt, likely, pess = t_shirt_to_days("M")
    assert opt == 2
    assert likely == 4
    assert pess == 8


def test_t_shirt_to_days_l():
    opt, likely, pess = t_shirt_to_days("L")
    assert opt == 4
    assert likely == 8
    assert pess == 16


def test_t_shirt_to_days_xl():
    opt, likely, pess = t_shirt_to_days("XL")
    assert opt == 8
    assert likely == 16
    assert pess == 32


def test_t_shirt_to_days_unknown():
    opt, likely, pess = t_shirt_to_days("unknown")
    assert opt == 1
    assert likely == 2
    assert pess == 4


def test_monte_carlo_returns_distribution():
    estimator = MonteCarloEstimator(iterations=1000)
    tasks = [
        TaskEstimate(task_id="T1", optimistic=1, likely=3, pessimistic=5),
        TaskEstimate(task_id="T2", optimistic=2, likely=4, pessimistic=8),
    ]
    result = estimator.simulate(tasks)
    assert result.p50 > 0
    assert result.p80 > result.p50
    assert result.p90 > result.p80
    assert result.p95 > result.p90
    assert result.mean > 0
    assert result.std_dev > 0


def test_monte_carlo_mean_is_reasonable():
    estimator = MonteCarloEstimator(iterations=1000)
    tasks = [
        TaskEstimate(task_id="T1", optimistic=1, likely=3, pessimistic=5),
    ]
    result = estimator.simulate(tasks)
    assert 2.5 <= result.mean <= 3.5


def test_high_variance_tasks():
    estimator = MonteCarloEstimator(iterations=100)
    tasks = [
        TaskEstimate(task_id="T1", optimistic=1, likely=3, pessimistic=5),
        TaskEstimate(task_id="T2", optimistic=1, likely=1, pessimistic=1.1),
    ]
    high_var = estimator.identify_high_variance_tasks(tasks, threshold=0.1)
    assert len(high_var) >= 1
    assert high_var[0][0] == "T1"