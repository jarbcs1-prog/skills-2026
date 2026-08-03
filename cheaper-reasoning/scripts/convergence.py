"""Convergence detection for contemplation sessions."""
from __future__ import annotations

from enum import Enum


class ConvergenceSignal(Enum):
    CONTINUE = "continue"
    CONVERGING = "converging"
    CONVERGED = "converged"
    STALLED = "stalled"


def detect_convergence(contemplation_history: list[str]) -> ConvergenceSignal:
    if len(contemplation_history) < 2:
        return ConvergenceSignal.CONTINUE

    recent = contemplation_history[-3:]
    themes = _extract_themes(recent)

    if _is_stalled(contemplation_history):
        return ConvergenceSignal.STALLED

    if _is_repeating(themes):
        return ConvergenceSignal.CONVERGED

    if _is_stabilizing(themes):
        return ConvergenceSignal.CONVERGING

    return ConvergenceSignal.CONTINUE


import re


def _extract_themes(segments: list[str]) -> list[set[str]]:
    return [set(re.findall(r'\b\w+\b', s.lower())) for s in segments]


def _is_repeating(themes: list[set[str]]) -> bool:
    if len(themes) < 2:
        return False
    overlap = themes[0].intersection(themes[1])
    if len(themes) >= 3:
        overlap = overlap.intersection(themes[2])
    return len(overlap) >= 2


def _is_stabilizing(themes: list[set[str]]) -> bool:
    if len(themes) < 2:
        return False
    for i in range(1, len(themes)):
        prev = themes[i - 1]
        curr = themes[i]
        new_words = curr - prev
        if len(new_words) > 3:
            return False
    return True


def _is_stalled(history: list[str]) -> bool:
    if len(history) < 4:
        return False
    recent = history[-4:]
    avg_length = sum(len(s) for s in recent) / len(recent)
    # Stalled: very short entries with minimal content
    return avg_length < 50