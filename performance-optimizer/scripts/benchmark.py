from __future__ import annotations

import json
import statistics
import time
from pathlib import Path
from typing import Any, Callable


class BenchmarkHarness:
    def __init__(self, baseline_file: Path | str = Path(".perf_baseline.json")) -> None:
        self.baseline_file = Path(baseline_file)

    def run(self, benchmark_callable: Callable[..., Any], warmup: int = 3, iterations: int = 10) -> dict:
        for _ in range(warmup):
            benchmark_callable()
        samples: list[float] = []
        for _ in range(iterations):
            start = time.perf_counter()
            benchmark_callable()
            samples.append((time.perf_counter() - start) * 1000.0)
        return {
            "mean_ms": statistics.mean(samples),
            "median_ms": statistics.median(samples),
            "min_ms": min(samples),
            "max_ms": max(samples),
            "samples": len(samples),
        }

    def compare(self, current: dict, baseline: dict, regression_threshold: float = 0.10) -> dict:
        current_mean = current["mean_ms"]
        baseline_mean = baseline["mean_ms"]
        if baseline_mean == 0:
            change_percent = 100.0 if current_mean > 0 else 0.0
        else:
            change_percent = (current_mean - baseline_mean) / abs(baseline_mean) * 100.0
        threshold = regression_threshold * 100.0
        if change_percent > threshold:
            status, regression = "regressed", True
        elif change_percent < -threshold:
            status, regression = "improved", False
        else:
            status, regression = "stable", False
        return {"regression": regression, "change_percent": change_percent, "status": status}

    def load_baselines(self) -> dict:
        if not self.baseline_file.exists():
            return {}
        return json.loads(self.baseline_file.read_text(encoding="utf-8"))

    def get_baseline(self, name: str) -> dict | None:
        return self.load_baselines().get(name)

    def store_baseline(self, name: str, result: dict) -> None:
        baselines = self.load_baselines()
        baselines[name] = result
        self.baseline_file.write_text(json.dumps(baselines, indent=2), encoding="utf-8")
