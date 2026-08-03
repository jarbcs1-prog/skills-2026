from __future__ import annotations

from typing import Any


def _ngrams(text: str) -> set[str]:
    lowered = text.lower()
    if not lowered:
        return set()
    if len(lowered) < 3:
        return {lowered}
    return {lowered[i : i + 3] for i in range(len(lowered) - 2)}


class SemanticDeduplicator:
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    def similarity(self, text_a: str, text_b: str) -> float:
        grams_a = _ngrams(text_a)
        grams_b = _ngrams(text_b)
        if not grams_a or not grams_b:
            return 0.0
        return len(grams_a & grams_b) / len(grams_a | grams_b)

    def is_duplicate(self, text_a: str, text_b: str) -> bool:
        return self.similarity(text_a, text_b) >= self.threshold

    def deduplicate(self, items: list[dict[str, Any]], key: str = "text") -> list[dict[str, Any]]:
        kept: list[dict[str, Any]] = []
        for item in items:
            if any(self.is_duplicate(item[key], existing[key]) for existing in kept):
                continue
            kept.append(item)
        return kept
