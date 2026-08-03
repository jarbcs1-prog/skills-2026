"""Translation memory for repeated phrase reuse."""

from __future__ import annotations

import json
from pathlib import Path


class TranslationMemory:
    """An exact-match translation memory keyed by source text."""

    def __init__(self, entries: list[dict] | None = None) -> None:
        self.entries: list[dict] = [dict(e) for e in (entries or [])]

    def add(self, source: str, translation: str, domain: str = "general") -> None:
        self.entries.append(
            {"source": source, "translation": translation, "domain": domain}
        )

    def lookup(self, source: str, domain: str | None = None) -> dict | None:
        for entry in self.entries:
            if entry["source"] == source:
                if domain is None or entry["domain"] == domain:
                    return dict(entry)
        return None

    def find_repeats(self, text: str, domain: str | None = None) -> list[dict]:
        """Return memory entries whose source appears inside ``text``."""
        return [
            dict(e)
            for e in self.entries
            if e["source"] in text and (domain is None or e["domain"] == domain)
        ]

    def hit_rate(self, texts: list[str]) -> float:
        """Fraction of input texts that have a memory hit (exact match)."""
        if not texts:
            return 0.0
        hits = sum(1 for t in texts if self.lookup(t) is not None)
        return hits / len(texts)

    def to_dict(self) -> list[dict]:
        return [dict(e) for e in self.entries]

    @classmethod
    def from_dict(cls, data: list) -> "TranslationMemory":
        return cls([dict(e) for e in data])

    def __len__(self) -> int:
        return len(self.entries)


def load_tm(path: str | Path) -> TranslationMemory:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return TranslationMemory.from_dict(data)


def save_tm(path: str | Path, tm: TranslationMemory) -> None:
    Path(path).write_text(
        json.dumps(tm.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
