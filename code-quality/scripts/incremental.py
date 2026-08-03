"""Incremental changed-file detection for the code-quality skill."""
from __future__ import annotations

import subprocess
from pathlib import Path

LANGUAGE_EXTENSIONS: dict[str, set[str]] = {
    "python": {".py"},
    "typescript": {".ts", ".tsx", ".js", ".jsx"},
    "rust": {".rs"},
    "go": {".go"},
}


def changed_files(base: str = "HEAD~1", extensions: list[str] | None = None) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(Path.cwd()), "diff", "--name-only", base],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    files = [line for line in result.stdout.splitlines() if line.strip()]
    if extensions:
        suffixes = set(extensions)
        files = [file for file in files if Path(file).suffix in suffixes]
    return sorted(files)


def filter_by_language(files: list[str], language: str) -> list[str]:
    extensions = LANGUAGE_EXTENSIONS.get(language)
    if extensions is None:
        return []
    return sorted(file for file in files if Path(file).suffix in extensions)
