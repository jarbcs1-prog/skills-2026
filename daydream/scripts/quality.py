from __future__ import annotations

import re
from typing import Any

ACTION_WORDS = frozenset(
    {
        "action",
        "apply",
        "build",
        "implement",
        "use",
        "adopt",
        "refactor",
        "automate",
        "improve",
    }
)

EVIDENCE_TERMS = ("per", "according to", "data", "shows", "%", "studies")

STOPWORDS = frozenset(
    {
        "a",
        "about",
        "above",
        "after",
        "again",
        "all",
        "am",
        "an",
        "and",
        "any",
        "are",
        "as",
        "at",
        "be",
        "because",
        "been",
        "before",
        "being",
        "below",
        "between",
        "both",
        "but",
        "by",
        "can",
        "did",
        "do",
        "does",
        "doing",
        "down",
        "during",
        "each",
        "few",
        "for",
        "from",
        "further",
        "had",
        "has",
        "have",
        "having",
        "he",
        "her",
        "here",
        "hers",
        "herself",
        "him",
        "himself",
        "his",
        "how",
        "i",
        "if",
        "in",
        "into",
        "is",
        "it",
        "its",
        "itself",
        "just",
        "me",
        "more",
        "most",
        "my",
        "myself",
        "no",
        "nor",
        "not",
        "now",
        "of",
        "off",
        "on",
        "once",
        "only",
        "or",
        "other",
        "our",
        "ours",
        "ourselves",
        "out",
        "over",
        "own",
        "same",
        "she",
        "should",
        "so",
        "some",
        "such",
        "than",
        "that",
        "the",
        "their",
        "theirs",
        "them",
        "themselves",
        "then",
        "there",
        "these",
        "they",
        "this",
        "those",
        "through",
        "to",
        "too",
        "under",
        "until",
        "up",
        "very",
        "was",
        "we",
        "were",
        "what",
        "when",
        "where",
        "which",
        "while",
        "who",
        "whom",
        "why",
        "with",
        "would",
        "you",
        "your",
        "yours",
        "yourself",
        "yourselves",
    }
)

_WORD_RE = re.compile(r"[a-zA-Z0-9]+")


def tokenize(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


def _clamp(value: float) -> float:
    return max(0.0, min(10.0, value))


def _has_evidence(text: str) -> bool:
    if any(char.isdigit() for char in text):
        return True
    if "%" in text or "according to" in text:
        return True
    tokens = set(tokenize(text))
    return any(term in tokens for term in ("per", "data", "shows", "studies"))


def score_insight(
    text: str,
    note_a_text: str,
    note_b_text: str,
    dimensions: dict[str, Any],
    threshold: float = 7.0,
) -> dict[str, Any]:
    insight_tokens = set(tokenize(text))
    source_tokens = set(tokenize(f"{note_a_text} {note_b_text}"))
    significant_source = {token for token in source_tokens if token not in STOPWORDS}

    overlap = len(insight_tokens & source_tokens) / len(insight_tokens) if insight_tokens else 0.0
    novelty = _clamp(10.0 * (1.0 - overlap))

    hits = sum(1 for word in ACTION_WORDS if word in insight_tokens)
    actionability = 10.0 if hits >= 2 else (5.0 if hits == 1 else 2.0)

    if significant_source:
        connectivity = _clamp(10.0 * (len(insight_tokens & significant_source) / len(significant_source)))
    else:
        connectivity = 0.0

    evidence = 10.0 if _has_evidence(text) else 3.0

    scores = {
        "novelty": novelty,
        "actionability": actionability,
        "connectivity": connectivity,
        "evidence": evidence,
    }
    weighted = sum(float(scores[dim]) * float(weight) for dim, weight in dimensions.items())
    return {
        "novelty": novelty,
        "actionability": actionability,
        "connectivity": connectivity,
        "evidence": evidence,
        "weighted": weighted,
        "passes": weighted >= threshold,
    }


def critique(
    insight_text: str,
    note_a_text: str,
    note_b_text: str,
    dimensions: dict[str, Any],
    threshold: float = 7.0,
) -> dict[str, Any]:
    scores = score_insight(insight_text, note_a_text, note_b_text, dimensions, threshold)
    if scores["passes"]:
        reason = f"Accepted: weighted score {scores['weighted']:.2f} meets threshold {threshold:.2f}."
    else:
        reason = f"Rejected: weighted score {scores['weighted']:.2f} below threshold {threshold:.2f}."
    return {"passed": scores["passes"], "scores": scores, "reason": reason}
