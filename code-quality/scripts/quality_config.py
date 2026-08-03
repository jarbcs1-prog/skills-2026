"""Configuration loading and validation for the code-quality skill."""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG: dict[str, Any] = {
    "version": 1,
    "languages": {
        "typescript": {
            "enabled": True,
            "typecheck": True,
            "lint": True,
            "format": True,
            "config": "tsconfig.json",
        },
        "python": {
            "enabled": True,
            "typecheck": "mypy",
            "lint": "ruff",
            "format": "black",
        },
        "rust": {
            "enabled": True,
            "check": "cargo check",
            "clippy": True,
            "format": "rustfmt",
        },
        "go": {
            "enabled": True,
            "vet": True,
            "lint": "golangci-lint",
            "format": "gofmt",
        },
    },
    "checks": {
        "markdown": {"enabled": True, "rules": ["no-trailing-whitespace", "no-missing-newline"]},
        "dependencies": {"enabled": False, "fail_on": "high"},
    },
    "thresholds": {
        "max_errors": 0,
        "max_warnings": 100,
        "fail_on_security": True,
    },
    "ignore": [
        "dist/",
        "build/",
        "*.generated.ts",
        "legacy/",
        "node_modules/",
        ".next/",
    ],
    "incremental": {
        "enabled": True,
        "base": "HEAD~1",
        "cache": True,
    },
    "reporting": {
        "format": "text",
        "output": None,
    },
}

CONFIG_FILENAME = ".code-quality.yml"


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    config_path = Path(path) if path is not None else Path(CONFIG_FILENAME)
    if not config_path.exists():
        return copy.deepcopy(DEFAULT_CONFIG)
    try:
        with config_path.open(encoding="utf-8") as stream:
            data = yaml.safe_load(stream)
    except OSError:
        return copy.deepcopy(DEFAULT_CONFIG)
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML in {config_path}: {exc}") from exc
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError(f"config root must be a mapping, got {type(data).__name__}")
    return _deep_merge(DEFAULT_CONFIG, data)


def validate_config(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(config, dict):
        return ["config must be a mapping"]

    for key in config:
        if key not in DEFAULT_CONFIG:
            errors.append(f"unknown top-level key: {key}")

    languages = config.get("languages")
    if languages is not None:
        if not isinstance(languages, dict):
            errors.append("languages must be a mapping")
        else:
            for lang_name, lang_config in languages.items():
                if not isinstance(lang_config, dict):
                    errors.append(f"languages.{lang_name} must be a mapping")

    checks = config.get("checks")
    if checks is not None:
        if not isinstance(checks, dict):
            errors.append("checks must be a mapping")
        else:
            for key in checks:
                if key not in ("markdown", "dependencies"):
                    errors.append(f"unknown checks key: {key}")
                # Accept both boolean and dict formats
                val = checks[key]
                if isinstance(val, bool):
                    pass  # Legacy boolean format
                elif isinstance(val, dict):
                    if not isinstance(val.get("enabled", True), bool):
                        errors.append(f"checks.{key}.enabled must be a boolean")
                else:
                    errors.append(f"checks.{key} must be a boolean or a mapping")

    thresholds = config.get("thresholds")
    if thresholds is not None:
        if not isinstance(thresholds, dict):
            errors.append("thresholds must be a mapping")
        else:
            for key in thresholds:
                if key not in ("max_errors", "max_warnings", "fail_on_security"):
                    errors.append(f"unknown thresholds key: {key}")
                if key == "max_errors" and not isinstance(thresholds[key], int):
                    errors.append("thresholds.max_errors must be an integer")
                if key == "max_warnings" and not isinstance(thresholds[key], int):
                    errors.append("thresholds.max_warnings must be an integer")
                if key == "fail_on_security" and not isinstance(thresholds[key], bool):
                    errors.append("thresholds.fail_on_security must be a boolean")

    ignore = config.get("ignore")
    if ignore is not None and (
        not isinstance(ignore, list) or not all(isinstance(item, str) for item in ignore)
    ):
        errors.append("ignore must be a list of strings")

    incremental = config.get("incremental")
    if incremental is not None:
        if not isinstance(incremental, dict):
            errors.append("incremental must be a mapping")
        else:
            if "enabled" in incremental and not isinstance(incremental["enabled"], bool):
                errors.append("incremental.enabled must be a boolean")
            if "base" in incremental and not isinstance(incremental["base"], str):
                errors.append("incremental.base must be a string")
            if "cache" in incremental and not isinstance(incremental["cache"], bool):
                errors.append("incremental.cache must be a boolean")

    reporting = config.get("reporting")
    if reporting is not None:
        if not isinstance(reporting, dict):
            errors.append("reporting must be a mapping")
        else:
            if "format" in reporting and not isinstance(reporting["format"], str):
                errors.append("reporting.format must be a string")

    return errors
