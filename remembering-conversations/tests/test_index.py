from __future__ import annotations

import json

from scripts.conversation_index import ConversationIndex


def make_conv(conversation_id: str, content: str, **kwargs: object) -> dict:
    conversation = {
        "conversation_id": conversation_id,
        "messages": [{"role": "user", "content": content}],
    }
    conversation.update(kwargs)
    return conversation


def test_add_and_all_ids(tmp_path) -> None:
    index = ConversationIndex(tmp_path / "cache")
    index.add(make_conv("b", "second conversation"))
    index.add(make_conv("a", "first conversation"))
    assert index.all_ids() == ["a", "b"]


def test_search_ranks_matching_first(tmp_path) -> None:
    index = ConversationIndex(tmp_path / "cache")
    index.add(make_conv("deploy", "We chose nginx for the production deployment."))
    index.add(make_conv("cookies", "Baking cookies needs butter, sugar and flour."))
    results = index.search("deployment configuration", top_k=10)
    ids = [result["conversation_id"] for result in results]
    assert ids[0] == "deploy"
    assert "cookies" in ids
    assert ids.index("deploy") < ids.index("cookies")
    assert results[0]["matched_messages"]


def test_since_filter_excludes_older(tmp_path) -> None:
    index = ConversationIndex(tmp_path / "cache")
    index.add(make_conv("old", "cache design discussion", timestamp="2026-01-05"))
    index.add(make_conv("new", "cache design discussion", timestamp="2026-06-15"))
    results = index.search("cache", since="2026-03-01", top_k=10)
    ids = [result["conversation_id"] for result in results]
    assert "new" in ids
    assert "old" not in ids


def test_get_summary_roundtrip(tmp_path) -> None:
    index = ConversationIndex(tmp_path / "cache")
    assert index.get_summary("missing") is None
    index.add(make_conv("s", "some content", summary="We decided to use FastAPI."))
    assert index.get_summary("s") == "We decided to use FastAPI."


def test_sync_imports_exports_once(tmp_path) -> None:
    index = ConversationIndex(tmp_path / "cache")
    export_dir = tmp_path / "exports"
    export_dir.mkdir()
    (export_dir / "one.json").write_text(
        json.dumps({"conversation_id": "one", "messages": [{"role": "user", "content": "hello"}]}),
        encoding="utf-8",
    )
    (export_dir / "multi.json").write_text(
        json.dumps(
            {
                "conversations": [
                    {"conversation_id": "m1", "messages": [{"role": "user", "content": "first"}]},
                    {"conversation_id": "m2", "messages": [{"role": "user", "content": "second"}]},
                ]
            }
        ),
        encoding="utf-8",
    )
    assert index.sync(export_dir) == 3
    assert index.sync(export_dir) == 0
    assert index.all_ids() == ["m1", "m2", "one"]
