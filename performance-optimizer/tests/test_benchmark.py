from __future__ import annotations

import time

from scripts.benchmark import BenchmarkHarness


def test_run_measures_positive_time() -> None:
    harness = BenchmarkHarness()
    result = harness.run(lambda: time.sleep(0.001), warmup=1, iterations=5)
    assert result["mean_ms"] > 0
    assert result["samples"] == 5
    assert result["median_ms"] > 0
    assert result["min_ms"] > 0
    assert result["max_ms"] >= result["min_ms"]


def test_compare_stable_identical() -> None:
    harness = BenchmarkHarness()
    result = harness.compare({"mean_ms": 10.0}, {"mean_ms": 10.0})
    assert result["status"] == "stable"
    assert result["regression"] is False
    assert result["change_percent"] == 0.0


def test_compare_regressed_slower_current() -> None:
    harness = BenchmarkHarness()
    result = harness.compare({"mean_ms": 15.0}, {"mean_ms": 10.0})
    assert result["status"] == "regressed"
    assert result["regression"] is True
    assert result["change_percent"] > 0


def test_compare_improved_faster_current() -> None:
    harness = BenchmarkHarness()
    result = harness.compare({"mean_ms": 8.0}, {"mean_ms": 10.0})
    assert result["status"] == "improved"
    assert result["regression"] is False
    assert result["change_percent"] < 0


def test_compare_threshold_respected() -> None:
    harness = BenchmarkHarness()
    result = harness.compare({"mean_ms": 10.5}, {"mean_ms": 10.0}, regression_threshold=0.10)
    assert result["status"] == "stable"


def test_baseline_roundtrip(tmp_path) -> None:
    harness = BenchmarkHarness(tmp_path / "baseline.json")
    harness.store_baseline("demo", {"mean_ms": 12.5, "samples": 10})
    loaded = harness.get_baseline("demo")
    assert loaded == {"mean_ms": 12.5, "samples": 10}
    assert harness.get_baseline("missing") is None
