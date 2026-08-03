"""Trigger conditions for cheaper-reasoning."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Task:
    complexity_score: float = 0.5
    uncertainty_level: float = 0.5
    requires_architecture_decision: bool = False
    has_conflicting_constraints: bool = False
    user_explicitly_requested_reasoning: bool = False


@dataclass
class ReasoningDecision:
    use: bool
    reason: str = ""
    confidence: float = 0.0


def should_use_deep_reasoning(task: Task) -> ReasoningDecision:
    triggers = [
        (task.complexity_score > 0.7, "high_complexity", 0.9),
        (task.uncertainty_level > 0.6, "high_uncertainty", 0.8),
        (task.requires_architecture_decision, "architecture_decision", 0.85),
        (task.has_conflicting_constraints, "conflicting_constraints", 0.75),
        (task.user_explicitly_requested_reasoning, "explicit_request", 1.0),
    ]

    triggered = [(t, r, c) for t, r, c in triggers if t]
    if not triggered:
        return ReasoningDecision(use=False)

    best = max(triggered, key=lambda x: x[2])
    return ReasoningDecision(use=True, reason=best[1], confidence=best[2])