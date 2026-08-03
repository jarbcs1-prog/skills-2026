"""Billing data models: subscribers, service plans and usage records."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional


@dataclass
class Subscriber:
    """A customer account."""

    subscriber_id: str
    account_number: str
    name: str
    phone_number: str
    email: str
    address: Dict[str, str] = field(default_factory=dict)
    plan_id: str = "PLAN-BASIC"
    status: str = "active"
    activation_date: datetime = field(default_factory=datetime.now)


@dataclass
class ServicePlan:
    """A recurring service bundle with allowances and overage rates."""

    plan_id: str
    name: str
    description: str
    monthly_fee: Decimal
    data_allowance_gb: float = 0.0
    voice_minutes: int = 0
    sms_count: int = 0
    overage_rates: Dict[str, Decimal] = field(default_factory=dict)


@dataclass
class UsageRecord:
    """A single metered usage event."""

    record_id: str
    subscriber_id: str
    usage_type: str
    timestamp: datetime
    quantity: float
    unit: str
    destination: Optional[str] = None
    charged: bool = False
