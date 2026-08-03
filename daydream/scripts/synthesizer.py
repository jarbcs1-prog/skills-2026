from __future__ import annotations

from collections import Counter
from typing import Any

from .quality import STOPWORDS, tokenize


def _significant(tokens: list[str]) -> set[str]:
    return {token for token in tokens if token not in STOPWORDS}


def _top_keyword(text: str) -> str:
    counts = Counter(token for token in tokenize(text) if token not in STOPWORDS)
    if not counts:
        return "none"
    return min(counts.items(), key=lambda item: (-item[1], item[0]))[0]


def synthesize_insight(note_a: dict[str, Any], note_b: dict[str, Any]) -> dict[str, Any]:
    title_a = note_a["title"]
    title_b = note_b["title"]
    shared = sorted(_significant(tokenize(note_a["text"])) & _significant(tokenize(note_b["text"])))
    shared_text = ", ".join(shared) if shared else "none"
    keyword_a = _top_keyword(note_a["text"])
    keyword_b = _top_keyword(note_b["text"])
    text = (
        f"Connecting {title_a} and {title_b}.\n\n"
        f"Shared themes: {shared_text}.\n\n"
        f"Suggested direction: {keyword_a}, {keyword_b}"
    )
    return {
        "title": f"Connection: {title_a} \u2194 {title_b}",
        "text": text,
        "sources": [note_a["path"], note_b["path"]],
    }
