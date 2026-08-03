"""AI text detection for human-writer-simulator skill."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class DetectionResult:
    ai_probability: float
    feature_scores: dict[str, float]
    confidence: float
    indicators: list[str]


class PerplexityFeature:
    def score(self, text: str) -> float:
        """Score based on perplexity-like metric (vocabulary diversity)."""
        words = text.lower().split()
        if not words:
            return 0.5
        unique = len(set(words))
        return 1.0 - (unique / max(1, len(words)))


class BurstinessFeature:
    def score(self, text: str) -> float:
        """Score based on sentence length variation (burstiness)."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) < 2:
            return 0.5
        lengths = [len(s.split()) for s in sentences]
        avg = sum(lengths) / len(lengths)
        if avg == 0:
            return 0.5
        variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
        return min(1.0, variance / 50)


class RepetitionFeature:
    def score(self, text: str) -> float:
        """Score based on word repetition."""
        words = text.lower().split()
        if not words:
            return 0.0
        from collections import Counter
        counts = Counter(words)
        max_count = max(counts.values())
        return min(1.0, max_count / max(1, len(words) * 0.1))


class TransitionFeature:
    def score(self, text: str) -> float:
        """Score based on transition word usage."""
        transitions = ["however", "therefore", "moreover", "furthermore", "consequently", "additionally", "nevertheless"]
        count = sum(1 for t in transitions if t in text.lower())
        return min(1.0, count / 3)


class VocabularyDiversityFeature:
    def score(self, text: str) -> float:
        """Score based on vocabulary diversity (type-token ratio)."""
        words = text.lower().split()
        if not words:
            return 0.5
        unique = len(set(words))
        return 1.0 - (unique / max(1, len(words)))


class SentenceStructureFeature:
    def score(self, text: str) -> float:
        """Score based on sentence structure uniformity."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) < 2:
            return 0.5
        starts = [s.split()[0].lower() if s.split() else "" for s in sentences]
        from collections import Counter
        counts = Counter(starts)
        most_common = counts.most_common(1)[0][1]
        return min(1.0, most_common / len(sentences))


class HedgingFeature:
    def score(self, text: str) -> float:
        """Score based on hedging language."""
        hedges = ["perhaps", "maybe", "possibly", "might", "could be", "it seems", "it appears", "roughly"]
        count = sum(1 for h in hedges if h in text.lower())
        return min(1.0, count / 3)


class StructureFeature:
    def score(self, text: str) -> float:
        """Score based on structural uniformity (bullet points, numbered lists)."""
        bullet_count = text.count("- ") + text.count("* ") + text.count("1.") + text.count("2.")
        if bullet_count > 3:
            return 1.0
        return 0.0


class AITextDetector:
    def __init__(self) -> None:
        self.features = [
            PerplexityFeature(),
            BurstinessFeature(),
            RepetitionFeature(),
            TransitionFeature(),
            VocabularyDiversityFeature(),
            SentenceStructureFeature(),
            HedgingFeature(),
            StructureFeature(),
        ]

    def analyze(self, text: str) -> DetectionResult:
        scores = {f.__class__.__name__: f.score(text) for f in self.features}
        ai_probability = self._classify(scores)
        confidence = self._confidence(scores)
        indicators = self._get_indicators(scores)
        return DetectionResult(
            ai_probability=ai_probability,
            feature_scores=scores,
            confidence=confidence,
            indicators=indicators,
        )

    def _classify(self, scores: dict[str, float]) -> float:
        weights = {
            "PerplexityFeature": 0.2,
            "BurstinessFeature": 0.2,
            "RepetitionFeature": 0.15,
            "TransitionFeature": 0.1,
            "VocabularyDiversityFeature": 0.15,
            "SentenceStructureFeature": 0.1,
            "HedgingFeature": 0.05,
            "StructureFeature": 0.05,
        }
        total = sum(scores.get(name, 0.0) * w for name, w in weights.items())
        return min(1.0, max(0.0, total))

    def _confidence(self, scores: dict[str, float]) -> float:
        values = list(scores.values())
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return min(1.0, 1.0 - variance)

    def _get_indicators(self, scores: dict[str, float]) -> list[str]:
        indicators = []
        if scores.get("PerplexityFeature", 0) > 0.5:
            indicators.append("low_vocabulary_diversity")
        if scores.get("BurstinessFeature", 0) < 0.2:
            indicators.append("uniform_sentence_length")
        if scores.get("RepetitionFeature", 0) > 0.5:
            indicators.append("high_repetition")
        if scores.get("TransitionFeature", 0) > 0.5:
            indicators.append("excessive_transitions")
        if scores.get("HedgingFeature", 0) > 0.3:
            indicators.append("hedging_language")
        if scores.get("StructureFeature", 0) > 0.5:
            indicators.append("structural_uniformity")
        return indicators


def detect_ai_text(text: str) -> dict:
    """Detect if text is likely AI-generated."""
    detector = AITextDetector()
    result = detector.analyze(text)
    return {
        "ai_probability": result.ai_probability,
        "confidence": result.confidence,
        "indicators": result.indicators,
        "is_ai_generated": result.ai_probability > 0.5,
    }
