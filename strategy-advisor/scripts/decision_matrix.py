"""Weighted decision matrix with sensitivity analysis for the strategy-advisor skill."""
from __future__ import annotations

import hashlib


class DecisionMatrix:
    def __init__(
        self,
        options: list[str],
        criteria: list[str],
        weights: list[float] | None = None,
    ) -> None:
        if weights is None:
            weights = [1.0] * len(criteria)
        elif len(weights) != len(criteria):
            raise ValueError("weights must match the number of criteria")
        self.options = list(options)
        self.criteria = list(criteria)
        self.weights = [float(w) for w in weights]

    def _pseudo_scores(self) -> dict[str, list[float]]:
        scores: dict[str, list[float]] = {}
        for option in self.options:
            scores[option] = [
                float(int(hashlib.md5(f"{option}:{criterion}".encode()).hexdigest(), 16) % 10 + 1)
                for criterion in self.criteria
            ]
        return scores

    def _normalized_scores(self, scores: dict[str, list[float]] | None = None) -> dict[str, list[float]]:
        scores = scores or self._pseudo_scores()
        for option in self.options:
            if option not in scores:
                raise ValueError(f"missing scores for option: {option}")
            if len(scores[option]) != len(self.criteria):
                raise ValueError(f"scores for {option!r} must match the number of criteria")
        normalized: dict[str, list[float]] = {option: [0.0] * len(self.criteria) for option in self.options}
        for j in range(len(self.criteria)):
            values = [scores[option][j] for option in self.options]
            lo, hi = min(values), max(values)
            for option in self.options:
                if hi == lo:
                    normalized[option][j] = 1.0
                else:
                    normalized[option][j] = (scores[option][j] - lo) / (hi - lo)
        return normalized

    def _totals(self, normalized: dict[str, list[float]], weights: list[float]) -> dict[str, float]:
        return {
            option: sum(normalized[option][j] * weights[j] for j in range(len(self.criteria)))
            for option in self.options
        }

    @staticmethod
    def _winner(totals: dict[str, float]) -> str:
        return max(totals, key=totals.get)

    def evaluate(self, scores: dict[str, list[float]] | None = None) -> dict:
        normalized = self._normalized_scores(scores)
        totals = self._totals(normalized, self.weights)
        ranking = sorted(self.options, key=lambda option: totals[option], reverse=True)
        return {
            "scores": totals,
            "ranking": ranking,
            "winner": ranking[0] if ranking else "",
            "normalized": normalized,
        }

    def sensitivity_analysis(self, step: float = 0.2) -> dict:
        base_winner = self._winner(self._totals(self._normalized_scores(), self.weights))
        normalized = self._normalized_scores()
        perturbations = []
        for i, criterion in enumerate(self.criteria):
            entry: dict = {"criterion": criterion, "weight": self.weights[i], "-step": {}, "+step": {}}
            changed = False
            for label, delta in (("-step", -step), ("+step", step)):
                weights = [max(0.0, w + (delta if j == i else 0.0)) for j, w in enumerate(self.weights)]
                total = sum(weights)
                if total <= 0:
                    weights = [1.0 / len(self.weights)] * len(self.weights)
                else:
                    weights = [w / total for w in weights]
                totals = self._totals(normalized, weights)
                entry[label] = totals
                if self._winner(totals) != base_winner:
                    changed = True
            entry["winner_change"] = changed
            perturbations.append(entry)
        return {
            "perturbations": perturbations,
            "stable_winner": not any(p["winner_change"] for p in perturbations),
        }

    def evaluate_with_sensitivity(self, step: float = 0.2) -> dict:
        result = self.evaluate()
        result["sensitivity"] = self.sensitivity_analysis(step)
        return result
