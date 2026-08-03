from __future__ import annotations

from scripts.auto_invoke import should_search


def test_trigger_how_should_i() -> None:
    assert should_search("How should I approach the cache design?")


def test_non_trigger() -> None:
    assert not should_search("Please pass the salt")


def test_trigger_best_way_to() -> None:
    assert should_search("What is the best way to structure the modules?")
