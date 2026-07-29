"""
Tests for bridge module.
"""

import sys
import os
import json
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from bridge import TokenBudget, RuntimeReflectionBridge
from storage import save_json


def test_token_budget_defaults():
    budget = TokenBudget()
    assert budget.max_capability_tokens == 500
    assert budget.avg_chars_per_token == 4.0
    print("PASS: token_budget_defaults")


def test_token_budget_custom():
    budget = TokenBudget(
        max_capability_tokens=200,
        avg_chars_per_token=3.0,
    )
    assert budget.max_capability_tokens == 200
    assert budget.avg_chars_per_token == 3.0
    print("PASS: token_budget_custom")


def test_get_active_capabilities_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        cap_path = Path(tmpdir) / "caps.json"
        save_json(cap_path, {"capabilities": []})

        import storage
        original = storage.CAPABILITY_MEMORY
        storage.CAPABILITY_MEMORY = cap_path

        try:
            bridge = RuntimeReflectionBridge()
            result = bridge.get_active_capabilities("general")
            assert result == []
        finally:
            storage.CAPABILITY_MEMORY = original
    print("PASS: get_active_capabilities_empty")


def test_get_active_capabilities_filters_inactive():
    with tempfile.TemporaryDirectory() as tmpdir:
        cap_path = Path(tmpdir) / "caps.json"
        save_json(cap_path, {
            "capabilities": [
                {
                    "name": "inactive-cap",
                    "principle": "test",
                    "scope": ["general"],
                    "active": False,
                    "promotion_level": "local",
                    "validation_score": 0.9,
                    "confidence": 0.9,
                },
                {
                    "name": "active-cap",
                    "principle": "test",
                    "scope": ["general"],
                    "active": True,
                    "promotion_level": "local",
                    "validation_score": 0.8,
                    "confidence": 0.8,
                },
            ]
        })

        import storage
        original = storage.CAPABILITY_MEMORY
        storage.CAPABILITY_MEMORY = cap_path

        try:
            bridge = RuntimeReflectionBridge()
            result = bridge.get_active_capabilities("general")
            assert len(result) == 1
            assert result[0]["name"] == "active-cap"
        finally:
            storage.CAPABILITY_MEMORY = original
    print("PASS: get_active_capabilities_filters_inactive")


def test_get_active_capabilities_scope_match():
    with tempfile.TemporaryDirectory() as tmpdir:
        cap_path = Path(tmpdir) / "caps.json"
        save_json(cap_path, {
            "capabilities": [
                {
                    "name": "cli-cap",
                    "principle": "test",
                    "scope": ["cli"],
                    "active": True,
                    "promotion_level": "local",
                    "validation_score": 0.7,
                    "confidence": 0.7,
                },
                {
                    "name": "api-cap",
                    "principle": "test",
                    "scope": ["api"],
                    "active": True,
                    "promotion_level": "local",
                    "validation_score": 0.7,
                    "confidence": 0.7,
                },
            ]
        })

        import storage
        original = storage.CAPABILITY_MEMORY
        storage.CAPABILITY_MEMORY = cap_path

        try:
            bridge = RuntimeReflectionBridge()
            result = bridge.get_active_capabilities("cli")
            assert len(result) == 1
            assert result[0]["name"] == "cli-cap"
        finally:
            storage.CAPABILITY_MEMORY = original
    print("PASS: get_active_capabilities_scope_match")


def test_get_active_capabilities_global_included():
    with tempfile.TemporaryDirectory() as tmpdir:
        cap_path = Path(tmpdir) / "caps.json"
        save_json(cap_path, {
            "capabilities": [
                {
                    "name": "global-cap",
                    "principle": "test",
                    "scope": ["specific-only"],
                    "active": True,
                    "promotion_level": "global",
                    "validation_score": 0.9,
                    "confidence": 0.9,
                },
            ]
        })

        import storage
        original = storage.CAPABILITY_MEMORY
        storage.CAPABILITY_MEMORY = cap_path

        try:
            bridge = RuntimeReflectionBridge()
            result = bridge.get_active_capabilities("unrelated-scope")
            assert len(result) == 1
            assert result[0]["name"] == "global-cap"
        finally:
            storage.CAPABILITY_MEMORY = original
    print("PASS: get_active_capabilities_global_included")


def test_get_active_capabilities_ranking():
    with tempfile.TemporaryDirectory() as tmpdir:
        cap_path = Path(tmpdir) / "caps.json"
        save_json(cap_path, {
            "capabilities": [
                {
                    "name": "low-score",
                    "principle": "test",
                    "scope": ["general"],
                    "active": True,
                    "promotion_level": "local",
                    "validation_score": 0.3,
                    "confidence": 0.3,
                },
                {
                    "name": "high-score",
                    "principle": "test",
                    "scope": ["general"],
                    "active": True,
                    "promotion_level": "local",
                    "validation_score": 0.9,
                    "confidence": 0.9,
                },
                {
                    "name": "mid-score",
                    "principle": "test",
                    "scope": ["general"],
                    "active": True,
                    "promotion_level": "local",
                    "validation_score": 0.6,
                    "confidence": 0.6,
                },
            ]
        })

        import storage
        original = storage.CAPABILITY_MEMORY
        storage.CAPABILITY_MEMORY = cap_path

        try:
            bridge = RuntimeReflectionBridge()
            result = bridge.get_active_capabilities("general")
            assert len(result) == 3
            assert result[0]["name"] == "high-score"
            assert result[1]["name"] == "mid-score"
            assert result[2]["name"] == "low-score"
        finally:
            storage.CAPABILITY_MEMORY = original
    print("PASS: get_active_capabilities_ranking")


def test_build_overlay_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        cap_path = Path(tmpdir) / "caps.json"
        save_json(cap_path, {"capabilities": []})

        import storage
        original = storage.CAPABILITY_MEMORY
        storage.CAPABILITY_MEMORY = cap_path

        try:
            bridge = RuntimeReflectionBridge()
            result = bridge.build_system_prompt_overlay("general")
            assert result == ""
        finally:
            storage.CAPABILITY_MEMORY = original
    print("PASS: build_overlay_empty")


def test_build_overlay_contains_header():
    with tempfile.TemporaryDirectory() as tmpdir:
        cap_path = Path(tmpdir) / "caps.json"
        save_json(cap_path, {
            "capabilities": [
                {
                    "name": "test-cap",
                    "principle": "Always verify",
                    "scope": ["general"],
                    "active": True,
                    "promotion_level": "local",
                    "validation_score": 0.8,
                    "confidence": 0.8,
                },
            ]
        })

        import storage
        original = storage.CAPABILITY_MEMORY
        storage.CAPABILITY_MEMORY = cap_path

        try:
            bridge = RuntimeReflectionBridge()
            result = bridge.build_system_prompt_overlay("general")
            assert "OPERATIONAL CONSTRAINTS" in result
            assert "[test-cap]" in result
            assert "Always verify" in result
        finally:
            storage.CAPABILITY_MEMORY = original
    print("PASS: build_overlay_contains_header")


def test_build_overlay_token_truncation():
    with tempfile.TemporaryDirectory() as tmpdir:
        cap_path = Path(tmpdir) / "caps.json"
        caps = []
        for i in range(50):
            caps.append({
                "name": f"cap-{i}",
                "principle": f"Principle number {i} with some extra text to make it longer",
                "scope": ["general"],
                "active": True,
                "promotion_level": "local",
                "validation_score": 0.5,
                "confidence": 0.5,
            })
        save_json(cap_path, {"capabilities": caps})

        import storage
        original = storage.CAPABILITY_MEMORY
        storage.CAPABILITY_MEMORY = cap_path

        try:
            budget = TokenBudget(
                max_capability_tokens=50,
                avg_chars_per_token=4.0,
            )
            bridge = RuntimeReflectionBridge(budget=budget)
            result = bridge.build_system_prompt_overlay("general")
            assert "cap-" in result
            assert "[cap-49]" not in result
        finally:
            storage.CAPABILITY_MEMORY = original
    print("PASS: build_overlay_token_truncation")


def test_build_overlay_default_budget():
    with tempfile.TemporaryDirectory() as tmpdir:
        cap_path = Path(tmpdir) / "caps.json"
        save_json(cap_path, {
            "capabilities": [
                {
                    "name": "default-cap",
                    "principle": "Test principle",
                    "scope": ["general"],
                    "active": True,
                    "promotion_level": "local",
                    "validation_score": 0.8,
                    "confidence": 0.8,
                },
            ]
        })

        import storage
        original = storage.CAPABILITY_MEMORY
        storage.CAPABILITY_MEMORY = cap_path

        try:
            bridge = RuntimeReflectionBridge()
            assert bridge.budget.max_capability_tokens == 500
            assert bridge.budget.avg_chars_per_token == 4.0
            result = bridge.build_system_prompt_overlay("general")
            assert "default-cap" in result
        finally:
            storage.CAPABILITY_MEMORY = original
    print("PASS: build_overlay_default_budget")


if __name__ == "__main__":
    test_token_budget_defaults()
    test_token_budget_custom()
    test_get_active_capabilities_empty()
    test_get_active_capabilities_filters_inactive()
    test_get_active_capabilities_scope_match()
    test_get_active_capabilities_global_included()
    test_get_active_capabilities_ranking()
    test_build_overlay_empty()
    test_build_overlay_contains_header()
    test_build_overlay_token_truncation()
    test_build_overlay_default_budget()
    print("\nAll bridge tests passed!")
