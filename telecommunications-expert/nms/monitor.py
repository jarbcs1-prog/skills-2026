"""Network monitoring: element lifecycle, metric collection, health scoring and alarms."""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from core.config import Config
from core.exceptions import ElementNotFoundError
from core.models import (
    AlarmSeverity,
    NetworkAlarm,
    NetworkElement,
    NetworkElementType,
    PerformanceMetric,
)

_DEFAULT_THRESHOLDS: Dict[str, tuple] = {
    "cpu_utilization": (70, 90),
    "memory_utilization": (80, 95),
    "eth0_traffic": (800, 950),
    "eth1_traffic": (800, 950),
}


@dataclass
class MetricViolation:
    """A single threshold breach recorded during monitoring."""

    metric_name: str
    value: float
    severity: str


@dataclass
class MonitorResult:
    """Outcome of monitoring one network element."""

    element_id: str
    status: str
    metrics: List[dict] = field(default_factory=list)
    violations: List[MetricViolation] = field(default_factory=list)
    health_score: float = 100.0

    def to_dict(self) -> dict:
        return {
            "element_id": self.element_id,
            "status": self.status,
            "metrics": self.metrics,
            "violations": [
                {
                    "metric_name": v.metric_name,
                    "value": v.value,
                    "severity": v.severity,
                }
                for v in self.violations
            ],
            "health_score": self.health_score,
        }


class NetworkManagementSystem:
    """Collects metrics, raises alarms and scores element health."""

    def __init__(self, seed: Optional[int] = None, config: Optional[Config] = None) -> None:
        self.network_elements: Dict[str, NetworkElement] = {}
        self.alarms: List[NetworkAlarm] = []
        self.performance_data: List[PerformanceMetric] = []
        self._rng = random.Random(seed)
        self._config = config

    def add_element(self, element: NetworkElement) -> None:
        self.network_elements[element.element_id] = element

    def get_element(self, element_id: str) -> NetworkElement:
        if element_id not in self.network_elements:
            raise ElementNotFoundError(f"element {element_id!r} not found")
        return self.network_elements[element_id]

    def monitor_network_element(self, element_id: str) -> dict:
        element = self.network_elements.get(element_id)
        if element is None:
            return {"error": "Network element not found"}
        metrics = self._collect_snmp_metrics(element)
        violations = self._evaluate_thresholds(metrics)
        health_score = self._calculate_health_score(element, violations)
        for violation in violations:
            if violation.severity == "critical":
                self._raise_alarm(
                    element,
                    AlarmSeverity.CRITICAL,
                    violation.metric_name,
                    f"{violation.metric_name} at {violation.value} exceeded critical threshold",
                )
        self.performance_data.extend(metrics)
        result = MonitorResult(
            element_id=element.element_id,
            status=element.status,
            metrics=[self._metric_to_dict(m) for m in metrics],
            violations=violations,
            health_score=health_score,
        )
        return result.to_dict()

    def _thresholds_for(self, metric: str, vendor: str) -> tuple:
        if self._config is not None:
            try:
                threshold = self._config.get_threshold(metric, vendor)
                return threshold.warning, threshold.critical
            except KeyError:
                pass
        return _DEFAULT_THRESHOLDS.get(metric, (0.0, 0.0))

    def _collect_snmp_metrics(self, element: NetworkElement) -> List[PerformanceMetric]:
        now = datetime.now()
        metrics: List[PerformanceMetric] = []
        spec = {
            "cpu_utilization": (self._get_cpu_utilization, "%"),
            "memory_utilization": (self._get_memory_utilization, "%"),
            "eth0_traffic": (self._get_interface_traffic, "Mbps"),
            "eth1_traffic": (self._get_interface_traffic, "Mbps"),
        }
        for metric_name, (sampler, unit) in spec.items():
            warning, critical = self._thresholds_for(metric_name, element.vendor)
            metrics.append(
                PerformanceMetric(
                    element_id=element.element_id,
                    metric_name=metric_name,
                    value=sampler(element),
                    unit=unit,
                    timestamp=now,
                    threshold_warning=warning,
                    threshold_critical=critical,
                )
            )
        return metrics

    def _evaluate_thresholds(self, metrics: List[PerformanceMetric]) -> List[MetricViolation]:
        violations: List[MetricViolation] = []
        for metric in metrics:
            if metric.value >= metric.threshold_critical:
                violations.append(MetricViolation(metric.metric_name, metric.value, "critical"))
            elif metric.value >= metric.threshold_warning:
                violations.append(MetricViolation(metric.metric_name, metric.value, "warning"))
        return violations

    def _calculate_health_score(
        self, element: NetworkElement, violations: List[MetricViolation]
    ) -> float:
        if element.status != "active":
            return 0.0
        score = 100.0
        for violation in violations:
            score -= 20.0 if violation.severity == "critical" else 10.0
        return max(0.0, score)

    def _raise_alarm(
        self,
        element: NetworkElement,
        severity: AlarmSeverity,
        alarm_type: str,
        description: str,
    ) -> NetworkAlarm:
        alarm = NetworkAlarm(
            alarm_id=self._generate_alarm_id(),
            element_id=element.element_id,
            severity=severity,
            alarm_type=alarm_type,
            description=description,
            timestamp=datetime.now(),
        )
        self.alarms.append(alarm)
        self._send_alarm_notification(alarm)
        return alarm

    def _send_alarm_notification(self, alarm: NetworkAlarm) -> None:
        # Notification delivery would integrate with email/SMS/SNMP traps.
        pass

    def _generate_alarm_id(self) -> str:
        return f"ALM-{uuid.uuid4().hex[:10].upper()}"

    def _get_cpu_utilization(self, element: NetworkElement) -> float:
        return self._rng.uniform(30, 70)

    def _get_memory_utilization(self, element: NetworkElement) -> float:
        return self._rng.uniform(40, 80)

    def _get_interface_traffic(self, element: NetworkElement) -> float:
        return self._rng.uniform(100, 800)

    def _metric_to_dict(self, metric: PerformanceMetric) -> dict:
        return {
            "metric_name": metric.metric_name,
            "value": metric.value,
            "unit": metric.unit,
            "status": "critical"
            if metric.value >= metric.threshold_critical
            else "warning"
            if metric.value >= metric.threshold_warning
            else "normal",
            "warning": metric.threshold_warning,
            "critical": metric.threshold_critical,
            "threshold_warning": metric.threshold_warning,
            "threshold_critical": metric.threshold_critical,
        }


def build_nms_from_config(config: Config) -> NetworkManagementSystem:
    nms = NetworkManagementSystem(config=config)
    for item in config.elements.get("network_elements", []):
        nms.add_element(
            NetworkElement(
                element_id=item["element_id"],
                element_type=NetworkElementType(item["element_type"]),
                name=item["name"],
                location=item.get("location", {}),
                ip_address=item["ip_address"],
                status=item.get("status", "active"),
                vendor=item.get("vendor", "Generic"),
                model=item.get("model", "unknown"),
                software_version=item.get("software_version", "unknown"),
                capacity=item.get("capacity", {}),
                utilization=item.get("utilization", {}),
            )
        )
    return nms
