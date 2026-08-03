from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG: dict[str, Any] = {
    "vault": {
        "path": ".",
        "max_age_days": 120,
        "include_patterns": ["*.md"],
        "exclude_patterns": [],
    },
    "sampling": {
        "pairs_per_run": 50,
        "recency_weight": 0.7,
        "diversity_weight": 0.3,
        "min_note_length": 100,
        "max_note_length": 5000,
    },
    "dimensions": {
        "novelty": 0.3,
        "actionability": 0.3,
        "connectivity": 0.2,
        "evidence": 0.2,
    },
    "quality": {"threshold": 7.0},
    "output": {
        "insight_dir": "Daydreams",
        "history_file": ".daydream_history.json",
        "graph_file": ".daydream_graph.graphml",
    },
    "scheduling": {"enabled": False, "max_runs_per_day": 1},
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: Path | None) -> dict[str, Any]:
    if path is None or not Path(path).exists():
        return copy.deepcopy(DEFAULT_CONFIG)
    try:
        with open(path, encoding="utf-8") as fh:
            loaded = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML config at {path}: {exc}") from exc
    if loaded is None:
        return copy.deepcopy(DEFAULT_CONFIG)
    if not isinstance(loaded, dict):
        raise ValueError(f"Config root at {path} must be a mapping")
    return _deep_merge(copy.deepcopy(DEFAULT_CONFIG), loaded)
