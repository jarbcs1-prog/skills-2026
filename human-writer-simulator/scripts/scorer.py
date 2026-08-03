"""Human-likeness scoring for human-writer-simulator skill."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class HumanScore:
    naturalness: float
    personality: float
    imperfection: float
    coherence: float
    emotional_range: float
    contextual_fit: float
    overall: float


class HumanLikenessScorer:
    DIMENSIONS = {
        "naturalness": 0.25,
        "personality": 0.20,
        "imperfection": 0.15,
        "coherence": 0.15,
        "emotional_range": 0.15,
        "contextual_fit": 0.10,
    }

    def score(self, text: str, style: str = "conversational") -> HumanScore:
        naturalness = self._score_naturalness(text)
        personality = self._score_personality(text)
        imperfection = self._score_imperfection(text)
        coherence = self._score_coherence(text)
        emotional_range = self._score_emotional_range(text)
        contextual_fit = self._score_contextual_fit(text, style)

        overall = (
            naturalness * 0.25
            + personality * 0.20
            + imperfection * 0.15
            + coherence * 0.15
            + emotional_range * 0.15
            + contextual_fit * 0.10
        )

        return HumanScore(
            naturalness=naturalness,
            personality=personality,
            imperfection=imperfection,
            coherence=coherence,
            emotional_range=emotional_range,
            contextual_fit=contextual_fit,
            overall=overall,
        )

    def _score_naturalness(self, text: str) -> float:
        """Score how naturally the text flows."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return 0.5
        # Check for varied sentence lengths
        lengths = [len(s.split()) for s in sentences]
        if len(lengths) < 2:
            return 0.5
        avg = sum(lengths) / len(lengths)
        variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
        return min(1.0, variance / 30)

    def _score_personality(self, text: str) -> float:
        """Score the presence of personal voice."""
        personal_markers = ["i ", "my ", "me ", "we ", "our ", "us ", "myself", "personally", "i think", "i feel", "i believe"]
        count = sum(1 for m in personal_markers if m in text.lower())
        return min(1.0, count / 3)

    def _score_imperfection(self, text: str) -> float:
        """Score the presence of controlled imperfections."""
        imperfection_markers = ["...", "uh", "um", "well", "actually", "you know", "like", "sort of", "kind of", "i mean"]
        count = sum(1 for m in imperfection_markers if m in text.lower())
        return min(1.0, count / 3)

    def _score_coherence(self, text: str) -> float:
        """Score logical coherence without being overly structured."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) < 2:
            return 0.5
        # Check for logical connectors
        connectors = ["because", "so", "then", "but", "however", "therefore", "since", "although"]
        count = sum(1 for c in connectors if c in text.lower())
        return min(1.0, count / len(sentences))

    def _score_emotional_range(self, text: str) -> float:
        """Score emotional variety."""
        emotional_words = ["excited", "frustrated", "happy", "sad", "angry", "hopeful", "worried", "confident", "uncertain", "amazing", "terrible", "wonderful"]
        count = sum(1 for w in emotional_words if w in text.lower())
        return min(1.0, count / 3)

    def _score_contextual_fit(self, text: str, style: str) -> float:
        """Score how well the text fits the target style."""
        style_markers = {
            "conversational": ["you know", "i mean", "like", "well", "sort of"],
            "technical": ["data", "analysis", "system", "process", "methodology"],
            "executive": ["strategy", "results", "outcome", "objective", "priority"],
            "creative": ["imagine", "perhaps", "vivid", "sudden", "whisper"],
        }
        markers = style_markers.get(style, style_markers["conversational"])
        count = sum(1 for m in markers if m in text.lower())
        return min(1.0, count / 2)


def score_human_likeness(text: str, style: str = "conversational") -> dict:
    """Score how human-like the text is."""
    scorer = HumanLikenessScorer()
    result = scorer.score(text, style)
    return {
        "overall": result.overall,
        "naturalness": result.naturalness,
        "personality": result.personality,
        "imperfection": result.imperfection,
        "coherence": result.coherence,
        "emotional_range": result.emotional_range,
        "contextual_fit": result.contextual_fit,
    }
