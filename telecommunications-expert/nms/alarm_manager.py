"""Alarm lifecycle management: filter, acknowledge, clear and query active alarms."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from core.models import AlarmSeverity, NetworkAlarm


class AlarmManager:
    """Stores and queries network alarms."""

    def __init__(self, alarms: Optional[List[NetworkAlarm]] = None) -> None:
        self.alarms: List[NetworkAlarm] = alarms if alarms is not None else []

    def add(self, alarm: NetworkAlarm) -> NetworkAlarm:
        self.alarms.append(alarm)
        return alarm

    def list_alarms(
        self,
        severity: Optional[AlarmSeverity] = None,
        since: Optional[datetime] = None,
    ) -> List[NetworkAlarm]:
        filtered = [
            alarm
            for alarm in self.alarms
            if (severity is None or alarm.severity == severity)
            and (since is None or alarm.timestamp >= since)
        ]
        return sorted(filtered, key=lambda a: a.timestamp, reverse=True)

    def acknowledge(self, alarm_id: str) -> bool:
        for alarm in self.alarms:
            if alarm.alarm_id == alarm_id:
                alarm.acknowledged = True
                return True
        return False

    def clear(self, alarm_id: str) -> bool:
        for alarm in self.alarms:
            if alarm.alarm_id == alarm_id:
                alarm.cleared = True
                alarm.clear_timestamp = datetime.now()
                return True
        return False

    def active_alarms(self) -> List[NetworkAlarm]:
        return [alarm for alarm in self.alarms if not alarm.cleared]


def parse_since(spec: str) -> datetime:
    """Parse a relative time spec like '30m', '1h', '24h' or '7d'."""
    spec = spec.strip().lower()
    if not spec or spec[-1] not in ("m", "h", "d"):
        raise ValueError(f"invalid since spec {spec!r}; expected e.g. 30m, 1h, 24h, 7d")
    try:
        amount = int(spec[:-1])
    except ValueError as exc:
        raise ValueError(f"invalid since spec {spec!r}") from exc
    if spec.endswith("m"):
        delta = timedelta(minutes=amount)
    elif spec.endswith("h"):
        delta = timedelta(hours=amount)
    else:
        delta = timedelta(days=amount)
    return datetime.now() - delta
