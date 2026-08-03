from __future__ import annotations

from scripts.profiler import Profiler

NESTED_SOURCE = '''def outer():
    for i in range(10):
        for j in range(10):
            for k in range(10):
                total += i * j * k
    return total
'''


def test_detect_returns_available_keys() -> None:
    tools = Profiler.detect("python")
    assert isinstance(tools, list)
    assert tools
    for entry in tools:
        assert "tool" in entry
        assert "available" in entry
        assert entry["available"] in (True, False)
    py_spy = next(entry for entry in tools if entry["tool"] == "py-spy")
    assert "available" in py_spy


def test_analyze_hotspots_keys() -> None:
    analysis = Profiler.analyze_hotspots(NESTED_SOURCE, "python")
    assert "hotspot_count" in analysis
    assert "functions_analyzed" in analysis
    assert "recommendations" in analysis
    assert "score" in analysis
    assert 0 <= analysis["score"] <= 100
    assert analysis["functions_analyzed"] == 1
    assert analysis["hotspot_count"] >= 1
    assert isinstance(analysis["recommendations"], list)
