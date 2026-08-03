from __future__ import annotations

from scripts.conversation_index import ConversationIndex
from scripts.pattern_detector import PatternDetector


def _build_index(tmp_path) -> ConversationIndex:
    index = ConversationIndex(tmp_path / "cache")
    for number in (1, 2):
        index.add(
            {
                "conversation_id": f"c{number}",
                "messages": [
                    {
                        "role": "user",
                        "content": f"We decided to refactor the api layer in conversation {number}.",
                    }
                ],
            }
        )
    return index


def test_detect_recurring_decisions(tmp_path) -> None:
    index = _build_index(tmp_path)
    decisions = PatternDetector(index).detect_recurring_decisions(top_k=10)
    by_term = {decision["term"]: decision for decision in decisions}
    assert by_term["refactor"]["conversations"] == 2
    assert by_term["refactor"]["conversation_ids"] == ["c1", "c2"]


def test_detect_architectural_patterns(tmp_path) -> None:
    index = _build_index(tmp_path)
    patterns = PatternDetector(index).detect_architectural_patterns(top_k=10)
    by_term = {pattern["term"]: pattern for pattern in patterns}
    assert by_term["api"]["conversations"] == 2
    assert by_term["api"]["conversation_ids"] == ["c1", "c2"]


def test_find_similar_situation(tmp_path) -> None:
    index = ConversationIndex(tmp_path / "cache")
    index.add(
        {
            "conversation_id": "x",
            "messages": [{"role": "user", "content": "We chose the cache-first architecture for reads."}],
        }
    )
    results = PatternDetector(index).find_similar_situation("cache-first architecture", top_k=5)
    assert results[0]["conversation_id"] == "x"
