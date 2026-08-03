"""Deterministic translation quality metrics (fluency, adequacy, consistency...)."""

from __future__ import annotations

import re

CURRENCY_PATTERN = re.compile(r"[¥$€£]\s?\d")
DATE_PATTERN = re.compile(r"\b\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}\b")

AI_TRANSITIONS = (
    "Additionally",
    "Furthermore",
    "Moreover",
    "In conclusion",
    "Overall",
    "Notably",
    "Specifically",
    "Importantly",
    "Consequently",
    "Hence",
    "Thus",
)


def bigram_jaccard(a: str, b: str) -> float:
    """Character bigram Jaccard similarity between two strings (0.0-1.0)."""
    ab = _bigrams(a)
    bb = _bigrams(b)
    if not ab and not bb:
        return 1.0
    if not ab or not bb:
        return 0.0
    inter = len(ab & bb)
    union = len(ab | bb)
    return inter / union if union else 0.0


def _bigrams(text: str) -> set[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) < 2:
        return {text} if text else set()
    return {text[i : i + 2] for i in range(len(text) - 1)}


def _sentence_lengths(text: str) -> list[int]:
    parts = [p.strip() for p in re.split(r"[.!?。！？]+", text)]
    return [len(p) for p in parts if p]


def _fluency(text: str) -> float:
    lengths = _sentence_lengths(text)
    if len(lengths) < 2:
        return 1.0
    mean = sum(lengths) / len(lengths)
    variance = sum((n - mean) ** 2 for n in lengths) / len(lengths)
    if mean <= 0:
        return 0.0
    return max(0.0, 1.0 - min(1.0, variance / (mean * mean)))


def _style_conformance(translation: str) -> float:
    sentences = [s.strip() for s in re.split(r"[.!?。！？]+", translation) if s.strip()]
    if not sentences:
        return 1.0
    ai_starts = sum(1 for s in sentences if s.startswith(AI_TRANSITIONS))
    return 1.0 - min(1.0, ai_starts / len(sentences))


def _cultural_appropriateness(source: str) -> float:
    if CURRENCY_PATTERN.search(source) or DATE_PATTERN.search(source):
        return 0.7
    return 1.0


def compute_quality_scores(
    source: str,
    translation: str,
    back_translation: str | None = None,
    glossary=None,
) -> dict:
    """Compute five quality dimensions, each 0.0-1.0.

    ``back_translation`` defaults to ``translation`` when not provided. All
    metrics are deterministic text statistics (no ML or network access).
    """
    bt = back_translation if back_translation is not None else translation

    fluency = _fluency(translation)
    adequacy = bigram_jaccard(source, bt)
    if glossary is not None:
        present = [t for t in glossary.terms if t in source]
        if present:
            consistent = sum(
                1 for t in present if glossary.terms[t]["translation"] in translation
            )
            terminology_consistency = consistent / len(present)
        else:
            terminology_consistency = 1.0
    else:
        terminology_consistency = 1.0
    style_conformance = _style_conformance(translation)
    cultural_appropriateness = _cultural_appropriateness(source)

    return {
        "fluency": round(fluency, 3),
        "adequacy": round(adequacy, 3),
        "terminology_consistency": round(terminology_consistency, 3),
        "style_conformance": round(style_conformance, 3),
        "cultural_appropriateness": round(cultural_appropriateness, 3),
    }


QUALITY_WEIGHTS = {
    "fluency": 0.25,
    "adequacy": 0.35,
    "terminology_consistency": 0.15,
    "style_conformance": 0.15,
    "cultural_appropriateness": 0.10,
}


def overall(scores: dict) -> float:
    """Weighted mean of the five quality dimensions (0.0-1.0)."""
    total = 0.0
    weight_sum = 0.0
    for name, weight in QUALITY_WEIGHTS.items():
        total += float(scores.get(name, 0.0)) * weight
        weight_sum += weight
    return total / weight_sum if weight_sum else 0.0
