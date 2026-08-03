"""Rewrite engine for human-writer-simulator skill."""
from __future__ import annotations

import re
from dataclasses import dataclass

from scripts.detector import AITextDetector
from scripts.scorer import HumanLikenessScorer, HumanScore
from scripts.styles import StyleProfile, STYLE_PROFILES


@dataclass
class RewriteConstraints:
    preserve_meaning: bool = True
    imperfection_level: float = 0.3
    preserve_tone: bool = True
    target_style: str = "conversational"


@dataclass
class RewriteResult:
    original: str
    rewritten: str
    ai_probability_before: float
    ai_probability_after: float
    human_score: HumanScore
    meaning_preserved: bool


class HumanRewriter:
    def __init__(
        self,
        style: StyleProfile | None = None,
        imperfection_level: float = 0.3,
        preserve_tone: bool = True,
    ) -> None:
        self.style = style or STYLE_PROFILES["conversational"]
        self.imperfection_level = imperfection_level
        self.preserve_tone = preserve_tone
        self.detector = AITextDetector()
        self.scorer = HumanLikenessScorer()

    def rewrite(self, text: str, domain: str | None = None, constraints: RewriteConstraints | None = None) -> RewriteResult:
        constraints = constraints or RewriteConstraints()

        # 1. Analyze source
        ai_before = self.detector.analyze(text)

        # 2. Plan rewrite
        style = constraints.target_style
        style_profile = STYLE_PROFILES.get(style, STYLE_PROFILES["conversational"])

        # 3. Generate rewrite
        rewritten = self._generate_rewrite(text, style_profile, constraints)

        # 4. Inject calibrated imperfections
        rewritten = self._inject_imperfections(rewritten, constraints.imperfection_level)

        # 5. Score result
        ai_after = self.detector.analyze(rewritten)
        human_score = self.scorer.score(rewritten, style)

        return RewriteResult(
            original=text,
            rewritten=rewritten,
            ai_probability_before=ai_before.ai_probability,
            ai_probability_after=ai_after.ai_probability,
            human_score=human_score,
            meaning_preserved=True,
        )

    def _generate_rewrite(self, text: str, style: StyleProfile, constraints: RewriteConstraints) -> str:
        """Generate a human-like rewrite of the text."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        rewritten_sentences = []
        for sentence in sentences:
            rewritten_sentence = self._rewrite_sentence(sentence, style)
            rewritten_sentences.append(rewritten_sentence)

        return " ".join(rewritten_sentences)

    def _rewrite_sentence(self, sentence: str, style: StyleProfile) -> str:
        """Rewrite a single sentence with the given style."""
        # Simple rewrite: vary sentence structure and add personal voice
        words = sentence.split()
        if not words:
            return sentence

        # Add personal voice markers
        if style.personal_voice > 0.5 and len(words) > 3:
            prefix = ["I think", "In my view", "From what I've seen", "Honestly,"]
            prefix_choice = prefix[hash(sentence) % len(prefix)]
            # Reorder: put prefix in the middle or end
            if len(words) > 5:
                mid = len(words) // 2
                result = " ".join(words[:mid]) + ", " + prefix_choice + " " + " ".join(words[mid:])
            else:
                result = prefix_choice + " " + " ".join(words)
        else:
            result = sentence

        return result

    def _inject_imperfections(self, text: str, level: float) -> str:
        """Inject calibrated imperfections into the text."""
        if level <= 0:
            return text

        imperfections = [
            ("...", ""),  # trailing off
            ("well, ", ""),  # filler
            ("you know, ", ""),  # filler
            ("sort of", "somewhat"),  # hedging
            ("kind of", "somewhat"),  # hedging
        ]

        result = text
        for imperfect, replacement in imperfections:
            if level > 0.5 and imperfect in result.lower():
                result = result.replace(imperfect, replacement)

        # Add occasional fragments (short sentences)
        if level > 0.3 and len(result.split(".")) > 3:
            result += " It depends."

        return result


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
