"""Quality validation for contemplation output."""
from __future__ import annotations


class QualityScore:
    def __init__(
        self,
        coherence: float = 0.0,
        progression: float = 0.0,
        self_correction: float = 0.0,
        insight_density: float = 0.0,
    ) -> None:
        self.coherence = coherence
        self.progression = progression
        self.self_correction = self_correction
        self.insight_density = insight_density

    def weighted_average(self) -> float:
        return (
            self.coherence * 0.25
            + self.progression * 0.25
            + self.self_correction * 0.25
            + self.insight_density * 0.25
        )

    def to_dict(self) -> dict:
        return {
            "coherence": self.coherence,
            "progression": self.progression,
            "self_correction": self.self_correction,
            "insight_density": self.insight_density,
            "weighted_average": self.weighted_average(),
        }


class ContemplationQuality:
    COHERENCE_WEIGHT = 0.25
    PROGRESSION_WEIGHT = 0.25
    SELF_CORRECTION_WEIGHT = 0.25
    INSIGHT_DENSITY_WEIGHT = 0.25

    def score(self, contemplation: str) -> QualityScore:
        lines = [l.strip() for l in contemplation.split("\n") if l.strip()]
        if not lines:
            return QualityScore()

        coherence = self._score_coherence(lines)
        progression = self._score_progression(lines)
        self_correction = self._score_self_correction(lines)
        insight_density = self._score_insight_density(lines)

        return QualityScore(
            coherence=coherence,
            progression=progression,
            self_correction=self_correction,
            insight_density=insight_density,
        )

    def _score_coherence(self, lines: list[str]) -> float:
        if len(lines) < 2:
            return 0.5
        transitions = sum(1 for l in lines if any(w in l.lower() for w in ["however", "but", "although", "therefore", "consequently", "furthermore", "moreover"]))
        return min(1.0, transitions / max(1, len(lines) * 0.3))

    def _score_progression(self, lines: list[str]) -> float:
        if len(lines) < 2:
            return 0.5
        unique_words = set()
        for l in lines:
            unique_words.update(l.lower().split())
        return min(1.0, len(unique_words) / max(1, len(lines) * 10))

    def _score_self_correction(self, lines: list[str]) -> float:
        corrections = sum(1 for l in lines if any(w in l.lower() for w in ["wait", "revise", "backtrack", "actually", "on second thought", "correction", "reconsider"]))
        return min(1.0, corrections / max(1, len(lines) * 0.2))

    def _score_insight_density(self, lines: list[str]) -> float:
        if not lines:
            return 0.0
        total_chars = sum(len(l) for l in lines)
        if total_chars == 0:
            return 0.0
        return min(1.0, total_chars / 10000)