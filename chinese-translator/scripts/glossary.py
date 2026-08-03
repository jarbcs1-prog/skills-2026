"""Terminology glossary management and consistency checking."""

from __future__ import annotations

import json
from pathlib import Path

TERM_SCHEMA = {"translation": str, "domain": str}


class Glossary:
    """A domain-tagged glossary mapping source terms to canonical translations."""

    def __init__(self, terms: dict[str, dict] | None = None) -> None:
        self.terms: dict[str, dict] = dict(terms or {})

    def add(self, term: str, translation: str, domain: str = "general") -> None:
        self.terms[term] = {"translation": translation, "domain": domain}

    def get(self, term: str) -> dict | None:
        return self.terms.get(term)

    def check(self, text: str) -> list[dict]:
        """Return violations: glossary terms present in ``text`` whose canonical
        translation does not appear alongside them."""
        violations: list[dict] = []
        for term, info in self.terms.items():
            if term not in text:
                continue
            if info["translation"] not in text:
                violations.append(
                    {
                        "term": term,
                        "translation": info["translation"],
                        "domain": info["domain"],
                        "issue": "registered translation not present in text",
                    }
                )
        return violations

    def to_dict(self) -> dict[str, dict]:
        return {k: dict(v) for k, v in self.terms.items()}

    @classmethod
    def from_dict(cls, data: dict) -> "Glossary":
        return cls({str(k): dict(v) for k, v in data.items()})

    def __len__(self) -> int:
        return len(self.terms)


def load_glossary(path: str | Path) -> Glossary:
    """Load a glossary from a JSON file. Raises FileNotFoundError when missing."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return Glossary.from_dict(data)


def save_glossary(path: str | Path, glossary: Glossary) -> None:
    Path(path).write_text(
        json.dumps(glossary.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
