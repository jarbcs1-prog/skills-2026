"""Estimation utilities for project-planner skill."""
from dataclasses import dataclass
from typing import List, Dict, Tuple
import random
import math


@dataclass
class TaskEstimate:
    task_id: str
    optimistic: float
    likely: float
    pessimistic: float

    @property
    def expected(self) -> float:
        return (self.optimistic + 4 * self.likely + self.pessimistic) / 6

    @property
    def variance(self) -> float:
        return ((self.pessimistic - self.optimistic) / 6) ** 2

    @property
    def std_dev(self) -> float:
        return math.sqrt(self.variance)


@dataclass
class EstimateDistribution:
    p50: float
    p80: float
    p90: float
    p95: float
    mean: float
    std_dev: float
    task_variances: Dict[str, float]


class MonteCarloEstimator:
    def __init__(self, iterations: int = 10000):
        self.iterations = iterations

    def simulate(self, tasks: List[TaskEstimate]) -> EstimateDistribution:
        total_samples = []
        task_contributions = {}

        for _ in range(self.iterations):
            total = 0.0
            for task in tasks:
                sample = random.triangular(task.optimistic, task.likely, task.pessimistic)
                total += sample
                task_contributions[task.task_id] = task_contributions.get(task.task_id, [])
                task_contributions[task.task_id].append(sample)
            total_samples.append(total)

        total_samples.sort()
        n = len(total_samples)

        return EstimateDistribution(
            p50=total_samples[int(n * 0.50)],
            p80=total_samples[int(n * 0.80)],
            p90=total_samples[int(n * 0.90)],
            p95=total_samples[int(n * 0.95)],
            mean=sum(total_samples) / n,
            std_dev=math.sqrt(sum((x - sum(total_samples) / n) ** 2 for x in total_samples) / n),
            task_variances={tid: sum(v) / len(v) for tid, v in task_contributions.items()},
        )

    def identify_high_variance_tasks(self, tasks: List[TaskEstimate],
                                      threshold: float = 0.2) -> List[Tuple[str, float]]:
        results = []
        for task in tasks:
            cv = task.std_dev / task.expected if task.expected > 0 else 0
            if cv > threshold:
                results.append((task.task_id, cv))
        return sorted(results, key=lambda x: x[1], reverse=True)


def three_point_estimate(optimistic: float, likely: float, pessimistic: float) -> TaskEstimate:
    return TaskEstimate(
        task_id="",
        optimistic=optimistic,
        likely=likely,
        pessimistic=pessimistic,
    )


def t_shirt_to_days(size: str) -> Tuple[float, float, float]:
    mapping = {
        "XS": (0.5, 1, 2),
        "S": (1, 2, 4),
        "M": (2, 4, 8),
        "L": (4, 8, 16),
        "XL": (8, 16, 32),
    }
    return mapping.get(size.upper(), (1, 2, 4))