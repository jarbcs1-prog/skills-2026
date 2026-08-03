"""Scenario planning and Monte Carlo analysis for the strategy-advisor skill."""
from __future__ import annotations

import random
import statistics

_DEFAULT_MULTIPLIERS = {"best": 1.2, "base": 1.0, "worst": 0.8}


def _is_numeric(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


class ScenarioPlanner:
    def __init__(self, base: dict) -> None:
        self.base = dict(base)

    def generate_scenarios(
        self,
        variations: dict[str, list[float]] | None = None,
        names: list[str] | None = None,
    ) -> dict:
        variations = variations or {}
        if names:
            scenario_names = list(names)
        else:
            counts = [len(v) for v in variations.values()] if variations else [3]
            n = max(3, *counts)
            scenario_names = ["best", "base", "worst"]
            while len(scenario_names) < n:
                scenario_names.append(f"scenario_{len(scenario_names) + 1}")
        scenarios = []
        for i, name in enumerate(scenario_names):
            variables: dict = {}
            for key, value in self.base.items():
                if not _is_numeric(value):
                    variables[key] = value
                    continue
                if key in variations:
                    multipliers = variations[key]
                    multiplier = multipliers[min(i, len(multipliers) - 1)]
                else:
                    multiplier = _DEFAULT_MULTIPLIERS.get(name, 1.0)
                variables[key] = value * multiplier
            description = _describe(name, i)
            scenarios.append({"name": name, "variables": variables, "description": description})
        return {"scenarios": scenarios, "count": len(scenarios)}

    def monte_carlo(self, iterations: int = 1000, seed: int = 42) -> dict:
        rng = random.Random(seed)
        metrics = []
        for _ in range(iterations):
            variables: dict = {}
            for key, value in self.base.items():
                if _is_numeric(value):
                    variables[key] = value * (1 + rng.gauss(0, 0.15))
                else:
                    variables[key] = value
            metrics.append(self._composite(variables))
        ordered = sorted(metrics)

        def quantile(p: float) -> float:
            return ordered[min(len(ordered) - 1, int(p * len(ordered)))]

        return {
            "iterations": iterations,
            "mean": statistics.mean(metrics),
            "median": statistics.median(metrics),
            "p5": quantile(0.05),
            "p95": quantile(0.95),
            "min": min(metrics),
            "max": max(metrics),
        }

    def _composite(self, variables: dict) -> float:
        values = []
        for key, value in variables.items():
            if not _is_numeric(value):
                continue
            base = self.base.get(key, 0)
            values.append(value / base if base else value)
        return statistics.mean(values) if values else 0.0


def _describe(name: str, index: int) -> str:
    if name == "best":
        return "Optimistic scenario: all numeric variables at 120% of base."
    if name == "base":
        return "Baseline scenario: variables unchanged from base."
    if name == "worst":
        return "Adverse scenario: all numeric variables at 80% of base."
    return f"Custom scenario {index + 1}: mixed variable assumptions."
