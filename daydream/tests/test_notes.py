from __future__ import annotations

from pathlib import Path

from scripts.daydream_config import DEFAULT_CONFIG
from scripts.notes import load_notes, sample_pairs


def _write_vault(root: Path) -> Path:
    vault = root / "vault"
    vault.mkdir()
    long_text = "Alpha note content. " * 20
    files = {
        "alpha.md": f"Alpha {long_text}",
        "beta.md": f"Beta {long_text}",
        "gamma.md": f"Gamma {long_text}",
        "tiny.md": "short",
    }
    for name, text in files.items():
        (vault / name).write_text(text, encoding="utf-8")
    return vault


def test_load_notes_returns_valid_notes_and_skips_short(tmp_path: Path) -> None:
    vault = _write_vault(tmp_path)
    notes = load_notes(vault, DEFAULT_CONFIG)
    assert len(notes) == 3
    assert {note["title"] for note in notes} == {"alpha", "beta", "gamma"}
    for note in notes:
        assert note["text"]
        assert isinstance(note["mtime"], float)
        assert note["path"].endswith(".md")


def test_load_notes_missing_vault_is_empty(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist"
    assert load_notes(missing, DEFAULT_CONFIG) == []


def test_sample_pairs_is_deterministic_and_disjoint(tmp_path: Path) -> None:
    vault = _write_vault(tmp_path)
    notes = load_notes(vault, DEFAULT_CONFIG)
    first = sample_pairs(notes, 2, seed=7)
    second = sample_pairs(notes, 2, seed=7)
    assert first == second
    assert all(a["path"] != b["path"] for a, b in first)
