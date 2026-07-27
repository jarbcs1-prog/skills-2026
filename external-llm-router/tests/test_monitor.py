"""Tests for external-llm-router scripts/monitor.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import monitor


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

class TestTrackUsage:
    def test_adds_tokens(self, tmp_path):
        usage_file = tmp_path / "usage.json"
        reached, total = monitor.track_usage(usage_file, 500, 10000)
        assert total == 500
        assert reached is False

    def test_cumulative(self, tmp_path):
        usage_file = tmp_path / "usage.json"
        monitor.track_usage(usage_file, 500, 10000)
        reached, total = monitor.track_usage(usage_file, 300, 10000)
        assert total == 800
        assert reached is False

    def test_limit_reached(self, tmp_path):
        usage_file = tmp_path / "usage.json"
        reached, total = monitor.track_usage(usage_file, 10001, 10000)
        assert reached is True
        assert total == 10001


class TestGetStatus:
    def test_status_read_only(self, tmp_path):
        usage_file = tmp_path / "usage.json"
        monitor.track_usage(usage_file, 500, 10000)
        reached, total = monitor.get_status(usage_file, 10000)
        assert total == 500
        # Second call should not change total
        _, total2 = monitor.get_status(usage_file, 10000)
        assert total2 == 500


class TestResetUsage:
    def test_reset(self, tmp_path):
        usage_file = tmp_path / "usage.json"
        monitor.track_usage(usage_file, 5000, 10000)
        monitor.reset_usage(usage_file)
        reached, total = monitor.get_status(usage_file, 10000)
        assert total == 0
        assert reached is False


class TestMaybeReset:
    def test_new_day_resets(self):
        data = {"total": 9999, "date": "2000-01-01"}
        result = monitor._maybe_reset(data)
        assert result["total"] == 0
        assert result["date"] != "2000-01-01"

    def test_same_day_no_reset(self):
        from datetime import date
        data = {"total": 500, "date": date.today().isoformat()}
        result = monitor._maybe_reset(data)
        assert result["total"] == 500


class TestLoadUsage:
    def test_missing_file(self, tmp_path):
        data = monitor._load_usage(tmp_path / "nonexistent.json")
        assert data["total"] == 0

    def test_corrupt_file(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not json {{{")
        data = monitor._load_usage(bad_file)
        assert data["total"] == 0

    def test_valid_file(self, tmp_path):
        good_file = tmp_path / "good.json"
        good_file.write_text(json.dumps({"total": 1234, "date": "2026-07-26"}))
        data = monitor._load_usage(good_file)
        assert data["total"] == 1234


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------

class TestCLI:
    def test_add_and_status(self, tmp_path):
        usage_file = tmp_path / "usage.json"
        # Add tokens — main() calls sys.exit(0) when under limit
        with pytest.raises(SystemExit) as exc_info:
            monitor.main(["--file", str(usage_file), "--add", "500", "--limit", "10000"])
        assert exc_info.value.code == 0
        # Check status
        reached, total = monitor.get_status(usage_file, 10000)
        assert total == 500

    def test_status_exits_1_when_limit_reached(self, tmp_path):
        usage_file = tmp_path / "usage.json"
        monitor.track_usage(usage_file, 10001, 10000)
        with pytest.raises(SystemExit) as exc_info:
            monitor.main(["--file", str(usage_file), "--status", "--limit", "10000"])
        assert exc_info.value.code == 1
