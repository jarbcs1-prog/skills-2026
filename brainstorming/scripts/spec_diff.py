"""Compare section headings between two design docs."""

from __future__ import annotations

import re
from pathlib import Path


def _sections(path: Path) -> set[str]:
    content = path.read_text(encoding="utf-8")
    found: set[str] = set()
    for line in content.splitlines():
        m = re.match(r"^#{1,3}\s+(.+)$", line.strip())
        if m:
            found.add(m.group(1).strip().rstrip("#").strip())
    return found


def diff_design_docs(base_path: Path, target_path: Path) -> dict:
    base = _sections(base_path)
    target = _sections(target_path)
    added = sorted(target - base)
    removed = sorted(base - target)
    return {
        "base": str(base_path),
        "target": str(target_path),
        "added_sections": added,
        "removed_sections": removed,
        "changed": bool(added or removed),
    }
