from __future__ import annotations

import fnmatch
import random
from pathlib import Path
from typing import Any

from .daydream_config import DEFAULT_CONFIG


def load_notes(vault: Path, config: dict[str, Any] | None = None) -> list[dict]:
    if config is None:
        config = DEFAULT_CONFIG
    vault_path = Path(vault)
    if not vault_path.exists() or not vault_path.is_dir():
        return []
    include_patterns = config["vault"]["include_patterns"]
    exclude_patterns = config["vault"]["exclude_patterns"]
    min_len = config["sampling"]["min_note_length"]
    max_len = config["sampling"]["max_note_length"]
    notes: list[dict] = []
    seen: set[str] = set()
    for pattern in include_patterns:
        for file_path in vault_path.rglob(pattern):
            if not file_path.is_file():
                continue
            rel = file_path.relative_to(vault_path).as_posix()
            if rel in seen:
                continue
            if any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(file_path.name, pat) for pat in exclude_patterns):
                continue
            try:
                text = file_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if not (min_len <= len(text) <= max_len):
                continue
            seen.add(rel)
            notes.append(
                {
                    "path": rel,
                    "title": file_path.stem,
                    "text": text,
                    "mtime": file_path.stat().st_mtime,
                }
            )
    return notes


def sample_pairs(notes: list[dict], pairs_per_run: int, seed: int | None) -> list[tuple[dict, dict]]:
    rng = random.Random(seed)
    combos = [(notes[i], notes[j]) for i in range(len(notes)) for j in range(i + 1, len(notes))]
    rng.shuffle(combos)
    return combos[:pairs_per_run]
