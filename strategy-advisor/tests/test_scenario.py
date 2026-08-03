"""Tests for scripts.scenario."""
from __future__ import annotations

import pytest

from scripts.scenario import ScenarioPlanner


def test_generate_scenarios_count_and_base():
    planner = ScenarioPlanner({"growth": 0.1, "cost": 5.0, "demand": 100.0})
    result = planner.generate_scenarios()
    assert result["count"] == len(result["scenarios"])
    assert result["count"] >= 3
    names = [s["name"] for s in result["scenarios"]]
    assert "base" in names
    base = [s for s in result["scenarios"] if s["name"] == "base"][0]
    assert base["variables"] == {"growth": 0.1, "cost": 5.0, "demand": 100.0}


def test_best_and_worst_multipliers():
    planner = ScenarioPlanner({"growth": 0.1, "cost": 5.0})
    scenarios = {s["name"]: s["variables"] for s in planner.generate_scenarios()["scenarios"]}
    assert scenarios["best"]["growth"] == pytest.approx(0.12)
    assert scenarios["best"]["cost"] == pytest.approx(6.0)
    assert scenarios["worst"]["growth"] == pytest.approx(0.08)
    assert scenarios["worst"]["cost"] == pytest.approx(4.0)


def test_generate_scenarios_with_variations():
    planner = ScenarioPlanner({"growth": 1.0, "cost": 1.0})
    result = planner.generate_scenarios(variations={"growth": [1.5, 1.0, 0.5]})
    scenarios = {s["name"]: s["variables"] for s in result["scenarios"]}
    assert scenarios["best"]["growth"] == 1.5
    assert scenarios["base"]["growth"] == 1.0
    assert scenarios["worst"]["growth"] == 0.5
    assert scenarios["best"]["cost"] == 1.2


def test_generate_scenarios_custom_names():
    planner = ScenarioPlanner({"growth": 1.0})
    result = planner.generate_scenarios(names=["bullish", "neutral", "bearish"])
    assert [s["name"] for s in result["scenarios"]] == ["bullish", "neutral", "bearish"]
    assert result["count"] == 3


def test_monte_carlo_distribution():
    planner = ScenarioPlanner({"growth": 0.1, "cost": 5.0})
    result = planner.monte_carlo(iterations=1000, seed=42)
    assert result["iterations"] == 1000
    assert result["p5"] < result["mean"] < result["p95"]
    assert result["min"] <= result["p5"]
    assert result["p95"] <= result["max"]


def test_monte_carlo_deterministic():
    planner = ScenarioPlanner({"growth": 0.1, "cost": 5.0})
    first = planner.monte_carlo(iterations=500, seed=7)
    second = planner.monte_carlo(iterations=500, seed=7)
    assert first == second
