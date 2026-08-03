"""Tests for test scaffolding."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.scaffolder import scaffold_test, LANGUAGE_EXTENSIONS


def test_scaffold_python():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = scaffold_test("python", "user authentication", Path(tmpdir))
        assert result["language"] == "python"
        assert result["test_file"].endswith("_test.py")
        assert Path(result["test_file"]).exists()


def test_scaffold_javascript():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = scaffold_test("javascript", "user auth", Path(tmpdir))
        assert result["language"] == "javascript"
        assert result["test_file"].endswith(".test.js")


def test_scaffold_rust():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = scaffold_test("rust", "retry logic", Path(tmpdir))
        assert result["language"] == "rust"
        assert result["test_file"].endswith("_test.rs")


def test_scaffold_go():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = scaffold_test("go", "retry logic", Path(tmpdir))
        assert result["language"] == "go"
        assert result["test_file"].endswith("_test.go")


def test_scaffold_java():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = scaffold_test("java", "user auth", Path(tmpdir))
        assert result["language"] == "java"
        assert result["test_file"].endswith("Test.java")


def test_scaffold_contains_test_functions():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = scaffold_test("python", "retry logic", Path(tmpdir))
        content = Path(result["test_file"]).read_text()
        assert "def test_" in content
        assert "retry_logic" in content


def test_language_extensions_defined():
    for lang, ext in LANGUAGE_EXTENSIONS.items():
        assert ext["test_suffix"]
        assert ext["source_ext"]