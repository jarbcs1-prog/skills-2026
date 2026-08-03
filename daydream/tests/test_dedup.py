from __future__ import annotations

from scripts.dedup import SemanticDeduplicator


def test_similarity_same_text_is_high() -> None:
    text = "The quick brown fox jumps over the lazy dog."
    assert SemanticDeduplicator().similarity(text, text) >= 0.85


def test_similarity_very_different_texts_is_low() -> None:
    deduper = SemanticDeduplicator()
    a = "The quick brown fox jumps over the lazy dog."
    b = "zzzz yyyy wwww vvvv uuuu tttt ssss rrrr qqqq"
    assert deduper.similarity(a, b) < 0.5


def test_is_duplicate_respects_threshold() -> None:
    deduper = SemanticDeduplicator(threshold=0.85)
    text = "the same note text repeated twice for length"
    assert deduper.is_duplicate(text, text)


def test_deduplicate_keeps_first_of_cluster() -> None:
    deduper = SemanticDeduplicator()
    items = [
        {"text": "The quick brown fox jumps over the lazy dog."},
        {"text": "The quick brown fox jumps over the lazy dog."},
        {"text": "Unrelated content entirely different words."},
    ]
    kept = deduper.deduplicate(items)
    assert len(kept) == 2
    assert kept[0]["text"] == items[0]["text"]
    assert kept[1]["text"] == items[2]["text"]
