"""Tests for language configurations."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.languages import LANGUAGE_CONFIGS, get_config, list_languages


def test_python_config():
    config = get_config("python")
    assert config is not None
    assert config.test_framework == "pytest"
    assert config.default_coverage_threshold == 0.8


def test_javascript_config():
    config = get_config("javascript")
    assert config is not None
    assert config.test_framework == "jest"


def test_rust_config():
    config = get_config("rust")
    assert config is not None
    assert config.test_framework == "cargo"


def test_go_config():
    config = get_config("go")
    assert config is not None
    assert config.test_framework == "go test"


def test_java_config():
    config = get_config("java")
    assert config is not None
    assert config.test_framework == "JUnit"


def test_get_unknown_language():
    config = get_config("unknown")
    assert config is None


def test_list_languages():
    langs = list_languages()
    assert "python" in langs
    assert "javascript" in langs
    assert "rust" in langs
    assert "go" in langs
    assert "java" in langs


def test_all_configs_have_required_fields():
    for name, config in LANGUAGE_CONFIGS.items():
        assert config.name == name
        assert config.test_framework
        assert config.test_command
        assert config.coverage_command
        assert config.mutation_command
        assert config.test_naming
        assert config.test_pattern