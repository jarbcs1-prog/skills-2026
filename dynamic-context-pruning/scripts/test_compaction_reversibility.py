"""Tests that compact → restore produces equivalent context.

Verifies the core promise of restorable compression: context compacted
via any strategy can be fully restored when paired with its offloaded data.
"""

import json
import os
import sys
import tempfile
import pytest
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(__file__))
from compaction import Compactor
from file_offloader import FileOffloader


def _make_tool_call(idx: int, tool: str = "bash", content: str = None) -> Dict[str, Any]:
    """Build a synthetic tool-call / tool-response pair."""
    return {
        "role": "assistant",
        "type": "tool_call",
        "tool": tool,
        "call_id": f"call_{idx:04d}",
        "input": {"command": f"echo step-{idx}"},
        "output": content or f"Output for step {idx}: completed successfully.",
    }


def _make_user_message(idx: int) -> Dict[str, Any]:
    return {
        "role": "user",
        "type": "message",
        "content": f"User instruction #{idx}: please do thing-{idx}",
    }


def _build_context(n: int) -> List[Dict[str, Any]]:
    """Build a context history with n interleaved user/assistant turns."""
    history: List[Dict[str, Any]] = []
    for i in range(n):
        history.append(_make_user_message(i))
        history.append(_make_tool_call(i))
    return history


@pytest.fixture
def sample_context():
    """Fixture: 30-turn context history."""
    return _build_context(30)


@pytest.fixture
def small_context():
    """Fixture: context shorter than keep_recent_full."""
    return _build_context(4)


@pytest.fixture
def offloader(tmp_path):
    """Fixture: FileOffloader backed by a temp directory."""
    return FileOffloader(
        base_path=str(tmp_path / "offload"),
        compression="gzip",
        index_format="jsonl",
    )


class TestCompactionIdentity:
    """Compact then restore should preserve order and completeness."""

    def test_compact_preserves_recent_tail(self, sample_context):
        """The most recent N turns must appear verbatim in compacted output."""
        compactor = Compactor(
            keep_recent_full=5, compact_ratio=0.5, preserve_structure=True
        )
        compacted, offloaded = compactor.compact(sample_context)

        assert len(compacted) >= 5
        assert compacted[-5:] == sample_context[-5:]

    def test_compact_reduces_length(self, sample_context):
        """Compaction must strictly reduce the context length."""
        compactor = Compactor(
            keep_recent_full=5, compact_ratio=0.5, preserve_structure=True
        )
        compacted, offloaded = compactor.compact(sample_context)

        assert len(compacted) < len(sample_context)
        assert len(offloaded) > 0

    def test_compact_returns_offloaded_data(self, sample_context):
        """Offloaded data must contain the removed items."""
        compactor = Compactor(
            keep_recent_full=5, compact_ratio=0.5, preserve_structure=True
        )
        compacted, offloaded = compactor.compact(sample_context)

        expected_offloaded = len(sample_context) - len(compacted)
        assert len(offloaded) == expected_offloaded

    def test_no_compaction_when_context_fits(self, small_context):
        """If context ≤ keep_recent_full, nothing should be compacted."""
        compactor = Compactor(
            keep_recent_full=10, compact_ratio=0.5, preserve_structure=True
        )
        compacted, offloaded = compactor.compact(small_context)

        assert compacted == small_context
        assert offloaded == []


class TestCompactionWithOffloading:
    """Round-trip: compact → offload → restore should recover all items."""

    def test_full_round_trip(self, sample_context, offloader):
        """Compact, offload, then restore and verify all items are present."""
        compactor = Compactor(
            keep_recent_full=5, compact_ratio=0.5, preserve_structure=True
        )
        compacted, offloaded = compactor.compact(sample_context)

        ref = offloader.offload(
            offloaded,
            metadata={"type": "tool_calls", "range": "0-25"},
        )

        restored_offloaded = offloader.restore(ref["path"])
        restored_context = compactor.restore(compacted, ref["path"])

        # Compacted portion should be intact
        assert restored_context == compacted

        # Offloaded portion should be fully recoverable
        assert len(restored_offloaded) == len(offloaded)
        for original, recovered in zip(offloaded, restored_offloaded):
            assert original == recovered

    def test_offloaded_data_survives_gzip(self, sample_context, offloader):
        """Gzip round-trip must not corrupt offloaded data."""
        compactor = Compactor(
            keep_recent_full=5, compact_ratio=0.5, preserve_structure=True
        )
        _, offloaded = compactor.compact(sample_context)

        ref = offloader.offload(
            offloaded, metadata={"type": "compressed", "range": "all"}
        )
        recovered = offloader.restore(ref["path"])

        assert json.dumps(recovered, sort_keys=True) == json.dumps(
            offloaded, sort_keys=True
        )

    def test_multiple_offload_restore_cycles(self, sample_context, offloader):
        """Repeated offload → restore cycles must not degrade data."""
        compactor = Compactor(
            keep_recent_full=5, compact_ratio=0.5, preserve_structure=True
        )
        _, offloaded = compactor.compact(sample_context)

        current = offloaded
        for _ in range(5):
            ref = offloader.offload(
                current, metadata={"type": "cycle", "range": "all"}
            )
            current = offloader.restore(ref["path"])

        assert len(current) == len(offloaded)
        for orig, cycle in zip(offloaded, current):
            assert orig == cycle


class TestCompactionStrategies:
    """Different compaction ratios should produce predictable output sizes."""

    @pytest.mark.parametrize(
        "ratio,expected_total_len",
        [
            (0.3, 43),  # 60 items → 55 old → keep 70% = 38 old + 5 recent = 43
            (0.5, 32),  # 60 items → 55 old → keep 50% = 27 old + 5 recent = 32
            (0.8, 15),  # 60 items → 55 old → keep 20% ≈ 10 old + 5 recent = 15 (float trunc)
        ],
        ids=["conservative-0.3", "balanced-0.5", "aggressive-0.8"],
    )
    def test_ratio_controls_output_size(self, ratio, expected_total_len):
        """Higher compact_ratio should yield proportionally shorter contexts."""
        context = _build_context(30)
        compactor = Compactor(
            keep_recent_full=5, compact_ratio=ratio, preserve_structure=True
        )
        compacted, _ = compactor.compact(context)
        assert len(compacted) == expected_total_len

    def test_hybrid_preserves_all_call_ids(self, sample_context):
        """Every call_id from the original must appear in compacted ∪ offloaded."""
        compactor = Compactor(
            keep_recent_full=5, compact_ratio=0.5, preserve_structure=True
        )
        compacted, offloaded = compactor.compact(sample_context)

        original_ids = {item.get("call_id") for item in sample_context if "call_id" in item}
        compacted_ids = {item.get("call_id") for item in compacted if "call_id" in item}
        offloaded_ids = {item.get("call_id") for item in offloaded if "call_id" in item}

        assert original_ids == (compacted_ids | offloaded_ids)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
