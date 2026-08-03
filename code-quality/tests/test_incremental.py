"""Tests for scripts.incremental."""
from __future__ import annotations

import subprocess
from pathlib import Path

from scripts import incremental


def test_filter_by_language_python() -> None:
    files = ["a.py", "b.ts", "c.py", "d.jsx"]
    assert incremental.filter_by_language(files, "python") == ["a.py", "c.py"]


def test_filter_by_language_typescript() -> None:
    files = ["a.py", "b.ts", "c.tsx", "d.js", "e.jsx", "f.rs"]
    assert incremental.filter_by_language(files, "typescript") == ["b.ts", "c.tsx", "d.js", "e.jsx"]


def test_filter_by_language_unknown_returns_empty() -> None:
    assert incremental.filter_by_language(["a.py", "b.ts"], "cobol") == []


def test_filter_by_language_sorts_result() -> None:
    files = ["z.py", "a.py"]
    assert incremental.filter_by_language(files, "python") == ["a.py", "z.py"]


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "a.py").write_text("x = 1\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "first commit")
    (repo / "a.py").write_text("x = 2\n", encoding="utf-8")
    (repo / "b.ts").write_text("const y = 1;\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "second commit")
    return repo


def test_changed_files_between_commits(tmp_path: Path, monkeypatch) -> None:
    repo = _make_repo(tmp_path)
    monkeypatch.chdir(repo)
    assert incremental.changed_files() == ["a.py", "b.ts"]


def test_changed_files_extension_filter(tmp_path: Path, monkeypatch) -> None:
    repo = _make_repo(tmp_path)
    monkeypatch.chdir(repo)
    assert incremental.changed_files(extensions=[".py"]) == ["a.py"]


def test_changed_files_git_failure_returns_empty(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert incremental.changed_files() == []
