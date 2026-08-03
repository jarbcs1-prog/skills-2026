from __future__ import annotations

from pathlib import Path

from scripts.graph import InsightGraph


def _note(path: str) -> dict:
    return {"path": path, "title": path[:-3], "text": "x" * 100, "mtime": 0.0}


def test_edges_from_insight_sources() -> None:
    notes = [_note("a.md"), _note("b.md"), _note("c.md")]
    insights = [{"sources": ["a.md", "b.md"]}, {"sources": ["b.md", "c.md"]}]
    graph = InsightGraph(notes, insights)
    assert len(graph.edges()) == 2
    assert ("a.md", "b.md") in graph.edges()
    assert ("b.md", "c.md") in graph.edges()


def test_export_graphml_writes_file(tmp_path: Path) -> None:
    notes = [_note("a.md"), _note("b.md"), _note("c.md")]
    insights = [{"sources": ["a.md", "b.md"]}]
    graph = InsightGraph(notes, insights)
    out = tmp_path / "graph.graphml"
    graph.export_graphml(out)
    content = out.read_text(encoding="utf-8")
    assert "<graphml" in content
    assert "<node" in content


def test_communities_cover_all_notes() -> None:
    notes = [_note("a.md"), _note("b.md"), _note("c.md")]
    insights = [{"sources": ["a.md", "b.md"]}, {"sources": ["b.md", "c.md"]}]
    graph = InsightGraph(notes, insights)
    communities = graph.communities()
    assert len(communities) >= 1
    covered = {node for members in communities.values() for node in members}
    assert covered == {"a.md", "b.md", "c.md"}
