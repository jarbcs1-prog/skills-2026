"""Design-doc section validation for the brainstorming skill."""

from __future__ import annotations

import re
from pathlib import Path

REQUIRED_SECTIONS = [
    "Purpose",
    "Scope",
    "Architecture",
    "Components",
    "Data Flow",
    "Error Handling",
    "Testing",
    "Tradeoffs Considered",
]


def _section_headings(content: str) -> list[str]:
    headings: list[str] = []
    for line in content.splitlines():
        m = re.match(r"^#{1,3}\s+(.+)$", line.strip())
        if m:
            headings.append(m.group(1).strip().rstrip("#").strip())
    return headings


def _normalize(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def validate_design_doc(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    normalized = {_normalize(h) for h in _section_headings(content)}
    present = [s for s in REQUIRED_SECTIONS if _normalize(s) in normalized]
    missing = [s for s in REQUIRED_SECTIONS if _normalize(s) not in normalized]
    return {
        "path": str(path),
        "valid": not missing,
        "missing_sections": missing,
        "present_sections": present,
    }
