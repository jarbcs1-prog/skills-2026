from __future__ import annotations

import math
from pathlib import Path

import pytest

from core.config import Config, ThresholdConfig

SKILL_ROOT = Path(__file__).parent.parent


def test_config_default_thresholds():
    config = Config(SKILL_ROOT / "config")
    threshold = config.get_threshold("cpu_utilization")
    assert threshold == ThresholdConfig(70.0, 90.0)
    assert config.get_threshold("memory_utilization") == ThresholdConfig(80.0, 95.0)


def test_config_vendor_override():
    config = Config(SKILL_ROOT / "config")
    assert config.get_threshold("cpu_utilization", "Cisco") == ThresholdConfig(75.0, 95.0)
    assert config.get_threshold("memory_utilization", "Cisco") == ThresholdConfig(85.0, 97.0)
    assert config.get_threshold("cpu_utilization", "Huawei") == ThresholdConfig(70.0, 90.0)


def test_config_unknown_metric_raises():
    config = Config(SKILL_ROOT / "config")
    with pytest.raises(KeyError):
        config.get_threshold("disk_utilization")


def test_config_missing_dir_returns_empty():
    config = Config(SKILL_ROOT / "does-not-exist")
    with pytest.raises(KeyError):
        config.get_threshold("cpu_utilization")


def test_config_vendor_profile():
    config = Config(SKILL_ROOT / "config")
    profile = config.get_vendor_profile("Cisco")
    assert profile is not None
    assert profile.name == "Cisco"
    assert profile.snmp_oids["cpu"]
    assert config.get_vendor_profile("Nokia") is None


def test_predict_capacity_exhaustion():
    from nms.capacity import predict_capacity_exhaustion

    assert predict_capacity_exhaustion(100.0, 120.0) == 0.0
    assert predict_capacity_exhaustion(100.0, 100.0) == 0.0
    assert predict_capacity_exhaustion(100.0, 50.0, growth_rate=0.15) > 0
    assert math.isinf(predict_capacity_exhaustion(100.0, 0.0))
    assert math.isinf(predict_capacity_exhaustion(100.0, 50.0, growth_rate=0.0))


def test_analyze_network_capacity():
    from core.models import NetworkElement, NetworkElementType
    from nms.capacity import analyze_network_capacity

    elements = {
        "NE-001": NetworkElement(
            element_id="NE-001",
            element_type=NetworkElementType.BASE_STATION,
            name="Site A",
            location={"region": "North", "city": "Metroville"},
            ip_address="10.0.1.11",
            capacity={"bandwidth_gbps": 10.0},
            utilization={"bandwidth_percent": 50.0},
        ),
        "NE-002": NetworkElement(
            element_id="NE-002",
            element_type=NetworkElementType.ROUTER,
            name="Router B",
            location={"region": "North", "city": "Metroville"},
            ip_address="10.0.1.12",
            capacity={"bandwidth_gbps": 20.0},
            utilization={"bandwidth_percent": 50.0},
        ),
        "NE-003": NetworkElement(
            element_id="NE-003",
            element_type=NetworkElementType.SWITCH,
            name="Switch C",
            location={"region": "South", "city": "Riverton"},
            ip_address="10.0.2.11",
            capacity={"bandwidth_gbps": 5.0},
            utilization={"bandwidth_percent": 10.0},
        ),
    }
    result = analyze_network_capacity(elements, "North")
    assert result["region"] == "North"
    assert result["total_capacity_gbps"] == 30.0
    assert result["used_capacity_gbps"] == 15.0
    assert result["utilization_percent"] == 50.0
    assert result["available_capacity_gbps"] == 15.0
    assert "expansion_recommended" in result

    missing = analyze_network_capacity(elements, "West")
    assert "error" in missing
