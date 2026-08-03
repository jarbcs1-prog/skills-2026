from __future__ import annotations

from scripts.synthesizer import synthesize_insight


def _note(path: str, title: str, text: str) -> dict:
    return {"path": path, "title": title, "text": text, "mtime": 0.0}


def test_synthesize_insight_shape() -> None:
    note_a = _note("a.md", "Alpha", "Improve automation using data and build small habits daily.")
    note_b = _note("b.md", "Beta", "Automate tasks to improve output and use proven methods per data studies.")
    insight = synthesize_insight(note_a, note_b)
    assert insight["title"] == "Connection: Alpha \u2194 Beta"
    assert insight["text"]
    assert "Shared themes:" in insight["text"]
    assert insight["sources"] == ["a.md", "b.md"]


def test_synthesize_insight_lists_shared_words() -> None:
    note_a = _note("a.md", "Alpha", "Improve automation using data and build small habits daily.")
    note_b = _note("b.md", "Beta", "Automate tasks to improve output and use proven methods per data studies.")
    insight = synthesize_insight(note_a, note_b)
    assert "improve" in insight["text"]
    assert "data" in insight["text"]


def test_synthesize_insight_no_shared_themes() -> None:
    note_a = _note("a.md", "Alpha", "One two three four five six seven eight nine ten eleven twelve.")
    note_b = _note("b.md", "Beta", "Red blue green yellow purple orange pink silver gold copper cyan.")
    insight = synthesize_insight(note_a, note_b)
    assert "Shared themes: none." in insight["text"]
