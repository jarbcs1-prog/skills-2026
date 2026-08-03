"""Configuration loading for thresholds, vendors, alerts, elements and billing data.

Uses PyYAML for parsing. If a configuration file is missing the loader returns
the provided default (typically an empty dict), so a partial config directory
still works.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

try:  # pragma: no cover - trivial
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


@dataclass
class ThresholdConfig:
    """Warning/critical thresholds for a single metric."""

    warning: float
    critical: float


@dataclass
class VendorProfile:
    """Device profile for a vendor."""

    name: str
    snmp_oids: Dict[str, str] = field(default_factory=dict)
    default_thresholds: Dict[str, ThresholdConfig] = field(default_factory=dict)
    cli_commands: Dict[str, str] = field(default_factory=dict)


class Config:
    """Loads and exposes YAML configuration files from a config directory."""

    def __init__(self, config_dir: Path | str = Path("config")) -> None:
        self.config_dir = Path(config_dir)
        self.thresholds: Dict[str, Any] = self._load("thresholds.yaml", {})
        self.vendors: Dict[str, Any] = self._load("vendors.yaml", {})
        self.alerts: Dict[str, Any] = self._load("alerts.yaml", {})
        self.elements: Dict[str, Any] = self._load("elements.yaml", {})
        self.subscribers: Dict[str, Any] = self._load("subscribers.yaml", {})
        self.plans: Dict[str, Any] = self._load("plans.yaml", {})

    def _load(self, filename: str, default: Any) -> Any:
        path = self.config_dir / filename
        if not path.exists():
            return default
        if yaml is None:
            raise RuntimeError(
                "PyYAML is required to load configuration files (pip install pyyaml)"
            )
        with path.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or default

    def get_threshold(self, metric: str, vendor: Optional[str] = None) -> ThresholdConfig:
        """Resolve a threshold for a metric, preferring a vendor-specific value."""
        if vendor:
            vendor_data = self.vendors.get(vendor, {})
            vendor_thresholds = vendor_data.get("default_thresholds", {}) or {}
            if metric in vendor_thresholds:
                entry = vendor_thresholds[metric]
                return ThresholdConfig(float(entry["warning"]), float(entry["critical"]))
        defaults = self.thresholds.get("defaults", {}) or {}
        if metric in defaults:
            entry = defaults[metric]
            return ThresholdConfig(float(entry["warning"]), float(entry["critical"]))
        raise KeyError(f"no threshold configured for {metric!r}")

    def get_vendor_profile(self, vendor: str) -> Optional[VendorProfile]:
        """Return a vendor profile if the vendor is configured, else None."""
        data = self.vendors.get(vendor)
        if not data:
            return None
        thresholds = {
            metric: ThresholdConfig(float(t["warning"]), float(t["critical"]))
            for metric, t in (data.get("default_thresholds", {}) or {}).items()
        }
        return VendorProfile(
            name=vendor,
            snmp_oids=dict(data.get("snmp_oids", {}) or {}),
            default_thresholds=thresholds,
            cli_commands=dict(data.get("cli_commands", {}) or {}),
        )
