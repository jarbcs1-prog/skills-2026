from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from core.config import Config
from core.exceptions import ElementNotFoundError, SNMPError
from core.models import AlarmSeverity, NetworkAlarm, NetworkElement, NetworkElementType
from nms.alarm_manager import AlarmManager, parse_since
from nms.monitor import NetworkManagementSystem, build_nms_from_config

SKILL_ROOT = Path(__file__).parent.parent


def _element(element_id: str = "NE-001") -> NetworkElement:
    return NetworkElement(
        element_id=element_id,
        element_type=NetworkElementType.BASE_STATION,
        name=f"Element {element_id}",
        location={"region": "North", "city": "Metroville"},
        ip_address="10.0.1.11",
        status="active",
        vendor="Cisco",
        capacity={"bandwidth_gbps": 10.0},
        utilization={"bandwidth_percent": 50.0},
    )


def test_monitor_active_element():
    nms = NetworkManagementSystem(seed=1)
    nms.add_element(_element())
    result = nms.monitor_network_element("NE-001")
    assert result["element_id"] == "NE-001"
    assert "health_score" in result
    assert len(result["metrics"]) == 4
    names = {m["metric_name"] for m in result["metrics"]}
    assert names == {"cpu_utilization", "memory_utilization", "eth0_traffic", "eth1_traffic"}
    assert nms.performance_data


def test_monitor_missing_element():
    nms = NetworkManagementSystem(seed=1)
    result = nms.monitor_network_element("NOPE")
    assert result["error"] == "Network element not found"


def test_get_element_raises():
    nms = NetworkManagementSystem()
    with pytest.raises(ElementNotFoundError):
        nms.get_element("NOPE")


def test_build_nms_from_config():
    nms = build_nms_from_config(Config(SKILL_ROOT / "config"))
    assert set(nms.network_elements) == {"NE-001", "NE-002", "NE-003"}
    assert nms.network_elements["NE-001"].vendor == "Cisco"


def test_monitor_inactive_element_zero_health():
    nms = NetworkManagementSystem(seed=1)
    element = _element()
    element.status = "maintenance"
    nms.add_element(element)
    result = nms.monitor_network_element("NE-001")
    assert result["health_score"] == 0.0


def test_alarm_manager_lifecycle():
    now = datetime.now()
    alarms = [
        NetworkAlarm(
            alarm_id="ALM-1",
            element_id="NE-001",
            severity=AlarmSeverity.CRITICAL,
            alarm_type="cpu",
            description="high cpu",
            timestamp=now - timedelta(hours=2),
        ),
        NetworkAlarm(
            alarm_id="ALM-2",
            element_id="NE-002",
            severity=AlarmSeverity.MINOR,
            alarm_type="mem",
            description="high mem",
            timestamp=now,
        ),
    ]
    manager = AlarmManager(alarms)
    assert [a.alarm_id for a in manager.list_alarms()] == ["ALM-2", "ALM-1"]
    assert manager.list_alarms(severity=AlarmSeverity.MINOR) == [alarms[1]]
    assert manager.list_alarms(since=now - timedelta(hours=1)) == [alarms[1]]
    assert manager.acknowledge("ALM-2")
    assert not manager.acknowledge("NOPE")
    assert manager.clear("ALM-2")
    assert alarms[1].cleared
    assert manager.active_alarms() == [alarms[0]]


def test_parse_since():
    spec = parse_since("1h")
    assert datetime.now() - timedelta(hours=1, minutes=1) < spec < datetime.now()
    with pytest.raises(ValueError):
        parse_since("banana")


def test_snmp_client_requires_pysnmp():
    from nms.snmp_client import SNMPClient

    client = SNMPClient("10.0.0.1")
    with pytest.raises(SNMPError):
        client.get("1.3.6.1.2.1.1.1.0")
