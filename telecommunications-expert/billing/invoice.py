"""Invoice generation: aggregate period usage charges and produce an invoice."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Tuple

from billing.models import ServicePlan, UsageRecord
from billing.processor import BillingSystem

_TAX_RATE = Decimal("0.10")
_DUE_DAYS = 15


class InvoiceGenerator:
    """Builds invoices for a subscriber over a billing period."""

    def __init__(self, billing_system: BillingSystem) -> None:
        self._billing = billing_system

    def generate_invoice(
        self, subscriber_id: str, billing_period: Tuple[datetime, datetime]
    ) -> dict:
        subscriber = self._billing.subscribers.get(subscriber_id)
        if subscriber is None:
            return {"error": "Subscriber not found"}
        plan = self._billing.service_plans.get(subscriber.plan_id)
        if plan is None:
            return {"error": "Service plan not found"}

        start_date, end_date = billing_period
        period_usage = [
            usage
            for usage in self._billing.usage_records
            if usage.subscriber_id == subscriber_id
            and start_date <= usage.timestamp <= end_date
        ]
        usage_charges = self._calculate_usage_charges(period_usage, plan)

        subtotal = plan.monthly_fee + usage_charges["total"]
        taxes = subtotal * _TAX_RATE
        total = subtotal + taxes

        invoice = {
            "invoice_id": self._generate_invoice_id(),
            "subscriber_id": subscriber_id,
            "billing_period": [start_date.isoformat(), end_date.isoformat()],
            "monthly_fee": float(plan.monthly_fee),
            "usage_charges": {
                k: float(v) for k, v in usage_charges.items() if k != "total"
            },
            "subtotal": float(subtotal),
            "taxes": float(taxes),
            "total": float(total),
            "due_date": (end_date + timedelta(days=_DUE_DAYS)).isoformat(),
        }
        self._billing.invoices.append(invoice)
        return invoice

    def _calculate_usage_charges(
        self, usage_records: List[UsageRecord], plan: ServicePlan
    ) -> dict:
        totals = {
            "data": sum(u.quantity for u in usage_records if u.usage_type == "data"),
            "voice": sum(u.quantity for u in usage_records if u.usage_type == "voice"),
            "sms": sum(u.quantity for u in usage_records if u.usage_type == "sms"),
        }
        data_overage = Decimal(str(max(0.0, totals["data"] - plan.data_allowance_gb))) * plan.overage_rates.get(
            "data_per_gb", Decimal("0")
        )
        voice_overage = Decimal(
            max(0, totals["voice"] - plan.voice_minutes)
        ) * plan.overage_rates.get("voice_per_minute", Decimal("0"))
        sms_overage = Decimal(max(0, totals["sms"] - plan.sms_count)) * plan.overage_rates.get(
            "sms_per_message", Decimal("0")
        )
        other = Decimal("0")
        total = data_overage + voice_overage + sms_overage + other
        return {
            "data": data_overage,
            "voice": voice_overage,
            "sms": sms_overage,
            "other": other,
            "total": total,
        }

    def _generate_invoice_id(self) -> str:
        return f"INV-{uuid.uuid4().hex[:10].upper()}"
