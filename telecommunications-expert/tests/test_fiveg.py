from __future__ import annotations

from fiveg.beamforming import BeamformingOptimizer
from fiveg.handover import HandoverManager
from fiveg.slice_manager import SliceManager


def test_configure_slice():
    result = SliceManager().configure_network_slice(
        {"name": "URLLC-slice", "slice_type": "urllc", "max_latency": 1}
    )
    assert result["status"] == "configured"
    assert result["resources_allocated"] is True
    assert result["slice_id"].startswith("SLICE-")


def test_configure_slice_invalid_type():
    result = SliceManager().configure_network_slice(
        {"name": "Bad", "slice_type": "hover"}
    )
    assert "error" in result


def test_beamforming():
    result = BeamformingOptimizer().optimize_beamforming(
        "BS-001", [[10, 10], [0, 5], {"x": -20, "y": 20}]
    )
    assert result["num_antennas"] == 64
    assert result["num_users"] == 3
    assert result["expected_throughput_improvement"] == 2.5
    assert len(result["beam_directions"]) == 3
    assert result["beam_directions"][0] == 45.0
    assert result["beam_directions"][1] == 90.0


def test_handover():
    result = HandoverManager(seed=1).manage_handover("UE-1", "CELL-A", "CELL-B")
    assert result["ue_id"] == "UE-1"
    assert result["handover"] in ("executed", "not_required")
    assert -110 <= result["source_rsrp"] <= -70
    assert -110 <= result["target_rsrp"] <= -70
