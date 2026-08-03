"""Shared dataclasses and enums for the telecommunications toolkit."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class NetworkElementType(Enum):
    """Type of physical or virtual network element."""

    BASE_STATION = "base_station"
    ROUTER = "router"
    SWITCH = "switch"
    FIBER_NODE = "fiber_node"
    GATEWAY = "gateway"
    FIREWALL = "firewall"


class AlarmSeverity(Enum):
    """Severity levels for network alarms."""

    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    WARNING = "warning"
    CLEARED = "cleared"


@dataclass
class NetworkElement:
    """A network device under management."""

    element_id: str
    element_type: NetworkElementType
    name: str
    location: Dict[str, str]
    ip_address: str
    status: str = "active"
    vendor: str = "Generic"
    model: str = "unknown"
    software_version: str = "unknown"
    capacity: Dict[str, float] = field(default_factory=dict)
    utilization: Dict[str, float] = field(default_factory=dict)


@dataclass
class NetworkAlarm:
    """An alarm raised against a network element."""

    alarm_id: str
    element_id: str
    severity: AlarmSeverity
    alarm_type: str
    description: str
    timestamp: datetime
    acknowledged: bool = False
    cleared: bool = False
    clear_timestamp: Optional[datetime] = None


@dataclass
class PerformanceMetric:
    """A collected performance measurement for an element."""

    element_id: str
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    threshold_warning: float
    threshold_critical: float


__all__ = [
    "NetworkElementType",
    "AlarmSeverity",
    "NetworkElement",
    "NetworkAlarm",
    "PerformanceMetric",
]
