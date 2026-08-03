"""Tests for scripts.quality_config."""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts import quality_config


def test_load_config_merges_thresholds_over_defaults(tmp_path: Path) -> None:
    config_path = tmp_path / ".code-quality.yml"
    config_path.write_text(
        "thresholds:\n  max_warnings: 5\n  max_errors: 1\n",
        encoding="utf-8",
    )
    config = quality_config.load_config(config_path)
    assert config["thresholds"]["max_warnings"] == 5
    assert config["thresholds"]["max_errors"] == 1
    assert config["thresholds"]["fail_on_security"] is True
    assert isinstance(config["languages"], dict)
    assert set(config["languages"].keys()) == {"typescript", "python", "rust", "go"}
    assert config["checks"]["markdown"]["enabled"] is True
    assert config["checks"]["dependencies"]["enabled"] is False
    assert isinstance(config["ignore"], list)


def test_load_config_missing_file_returns_defaults(tmp_path: Path) -> None:
    config = quality_config.load_config(tmp_path / "missing.yml")
    assert config == quality_config.DEFAULT_CONFIG


def test_load_config_invalid_yaml_raises_value_error(tmp_path: Path) -> None:
    config_path = tmp_path / "bad.yml"
    config_path.write_text("thresholds: [unclosed\n", encoding="utf-8")
    with pytest.raises(ValueError):
        quality_config.load_config(config_path)


def test_validate_config_valid_defaults() -> None:
    assert quality_config.validate_config(dict(quality_config.DEFAULT_CONFIG)) == []


def test_validate_config_flags_unknown_top_level_key() -> None:
    errors = quality_config.validate_config({"bogus": True})
    assert any("bogus" in error for error in errors)


def test_validate_config_flags_wrong_type_thresholds() -> None:
    errors = quality_config.validate_config({"thresholds": {"max_errors": "zero"}})
    assert any("max_errors" in error for error in errors)


def test_validate_config_flags_non_mapping_thresholds() -> None:
    errors = quality_config.validate_config({"thresholds": "nope"})
    assert any("thresholds" in error for error in errors)
