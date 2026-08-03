from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
NOW = datetime.now().strftime("%Y-%m")


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "scripts.cli", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(ROOT),
    )


def test_nms_monitor():
    result = run_cli("nms", "monitor", "--element", "NE-001")
    assert result.returncode == 0
    assert "element_id" in result.stdout
    assert "health_score" in result.stdout


def test_nms_monitor_missing_element():
    result = run_cli("nms", "monitor", "--element", "NOPE")
    assert result.returncode == 1
    assert "Network element not found" in result.stdout


def test_nms_alarms():
    result = run_cli("nms", "alarms")
    assert result.returncode == 0
    assert "alarms" in result.stdout


def test_nms_capacity():
    result = run_cli("nms", "capacity", "--region", "North")
    assert result.returncode == 0
    assert "total_capacity_gbps" in result.stdout


def test_nms_capacity_unknown_region():
    result = run_cli("nms", "capacity", "--region", "West")
    assert result.returncode == 1
    assert "No network elements in region" in result.stdout


def test_billing_process(tmp_path):
    usage_file = tmp_path / "usage.csv"
    usage_file.write_text(
        "record_id,subscriber_id,usage_type,timestamp,quantity,unit\n"
        f"R1,SUB-001,data,{datetime.now().isoformat()},15.0,GB\n"
        f"R2,SUB-001,data,{datetime.now().isoformat()},10.0,GB\n",
        encoding="utf-8",
    )
    result = run_cli("billing", "process", "--usage-file", str(usage_file))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data) == 2
    assert data[0]["within_allowance"] is True
    assert data[0]["charge"] == 0.0
    assert data[1]["within_allowance"] is False
    assert data[1]["charge"] == 50.0


def test_billing_process_missing_file():
    result = run_cli("billing", "process", "--usage-file", "nope.csv")
    assert result.returncode == 1
    assert "not found" in result.stdout


def test_billing_invoice():
    result = run_cli("billing", "invoice", "--subscriber", "SUB-001", "--period", NOW)
    assert result.returncode == 0
    assert "invoice_id" in result.stdout


def test_billing_invoice_unknown_subscriber():
    result = run_cli("billing", "invoice", "--subscriber", "NOPE", "--period", NOW)
    assert result.returncode == 1
    assert "Subscriber not found" in result.stdout


def test_fiveg_slice_create():
    result = run_cli("fiveg", "slice", "create", "--name", "URLLC-slice", "--type", "urllc")
    assert result.returncode == 0
    assert "slice_id" in result.stdout
    assert "configured" in result.stdout


def test_fiveg_slice_bad_type():
    result = run_cli("fiveg", "slice", "create", "--name", "X", "--type", "hover")
    assert result.returncode == 1
    assert "unknown slice type" in result.stdout


def test_fiveg_beamforming(tmp_path):
    positions = tmp_path / "positions.json"
    positions.write_text("[[10, 10], [0, 5], [-20, 20]]", encoding="utf-8")
    result = run_cli("fiveg", "beamforming", "--bs", "BS-001", "--users", str(positions))
    assert result.returncode == 0
    assert "num_antennas" in result.stdout


def test_fiveg_beamforming_missing_file():
    result = run_cli("fiveg", "beamforming", "--bs", "BS-001", "--users", "nope.json")
    assert result.returncode == 1
    assert "not found" in result.stdout


def test_fiveg_handover():
    result = run_cli("fiveg", "handover", "--ue", "UE-1", "--source", "A", "--target", "B")
    assert result.returncode == 0
    assert "ue_id" in result.stdout


def test_api_serve_help():
    result = run_cli("api", "serve", "--help")
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_no_command_fails():
    result = run_cli()
    assert result.returncode != 0


def test_unknown_action_fails():
    result = run_cli("nms", "frobnicate")
    assert result.returncode != 0
