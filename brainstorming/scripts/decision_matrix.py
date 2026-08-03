"""Deterministic weighted decision-matrix scoring."""

from __future__ import annotations

import hashlib

SENSITIVITY_RANGE = 0.2


def _pseudo_score(option: str, criterion: str) -> float:
    digest = hashlib.sha256(f"{option}|{criterion}".encode("utf-8")).hexdigest()
    return float(int(digest[:8], 16) % 10) + 1.0


def _normalize_column(values: list[float]) -> list[float]:
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return [1.0] * len(values)
    return [(v - lo) / (hi - lo) for v in values]


def _score_row(
    normalized: list[list[float]], index: int, weights: list[float], scale: float = 1.0
) -> float:
    return sum(normalized[j][index] * weights[j] for j in range(len(weights))) * scale


def evaluate(
    options: list[str],
    criteria: list[str],
    weights: list[float],
    scores_matrix: list[list[float]] | None = None,
) -> dict:
    if len(criteria) != len(weights):
        raise ValueError("criteria and weights must have the same length")
    if scores_matrix is not None and len(scores_matrix) != len(options):
        raise ValueError("scores_matrix must have one row per option")
    matrix = scores_matrix if scores_matrix is not None else [
        [_pseudo_score(option, criterion) for criterion in criteria]
        for option in options
    ]
    normalized = [
        _normalize_column([row[column] for row in matrix]) for column in range(len(criteria))
    ]
    scores = {
        option: sum(normalized[j][i] * weights[j] for j in range(len(criteria)))
        for i, option in enumerate(options)
    }
    ranking = sorted(options, key=lambda o: scores[o], reverse=True)
    sensitivity = {
        option: {
            "low": _score_row(normalized, i, weights, 1.0 - SENSITIVITY_RANGE),
            "high": _score_row(normalized, i, weights, 1.0 + SENSITIVITY_RANGE),
        }
        for i, option in enumerate(options)
    }
    return {
        "scores": scores,
        "ranking": ranking,
        "winner": ranking[0],
        "sensitivity": sensitivity,
    }
