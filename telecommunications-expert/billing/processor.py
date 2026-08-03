"""Usage processing: apply usage against allowances and compute charges."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from billing.models import ServicePlan, Subscriber, UsageRecord
from core.config import Config


class BillingSystem:
    """Processes subscriber usage records against service plan allowances."""

    def __init__(self) -> None:
        self.subscribers: Dict[str, Subscriber] = {}
        self.service_plans: Dict[str, ServicePlan] = {}
        self.usage_records: List[UsageRecord] = []
        self.invoices: List[dict] = []

    def add_subscriber(self, subscriber: Subscriber) -> None:
        self.subscribers[subscriber.subscriber_id] = subscriber

    def add_plan(self, plan: ServicePlan) -> None:
        self.service_plans[plan.plan_id] = plan

    def process_usage(self, usage: UsageRecord) -> dict:
        subscriber = self.subscribers.get(usage.subscriber_id)
        if subscriber is None:
            return {"error": "Subscriber not found"}
        if subscriber.status != "active":
            return {"error": "Subscriber not active"}
        plan = self.service_plans.get(subscriber.plan_id)
        if plan is None:
            return {"error": "Service plan not found"}

        current_usage = self._get_current_month_usage(usage.subscriber_id, usage.usage_type)
        allowance, rate = self._allowance_and_rate(plan, usage.usage_type)
        within_allowance = current_usage <= allowance
        charge = float(usage.quantity) * float(rate) if not within_allowance else 0.0

        usage.charged = True
        self.usage_records.append(usage)
        return {
            "subscriber_id": usage.subscriber_id,
            "usage_type": usage.usage_type,
            "quantity": usage.quantity,
            "charge": charge,
            "within_allowance": within_allowance,
        }

    def _get_current_month_usage(self, subscriber_id: str, usage_type: str) -> float:
        total = 0.0
        for record in self.usage_records:
            month_start = datetime(record.timestamp.year, record.timestamp.month, 1)
            if (
                record.subscriber_id == subscriber_id
                and record.usage_type == usage_type
                and record.timestamp >= month_start
            ):
                total += record.quantity
        return total

    def _allowance_and_rate(self, plan: ServicePlan, usage_type: str):
        allowances = {
            "data": plan.data_allowance_gb,
            "voice": plan.voice_minutes,
            "sms": plan.sms_count,
        }
        rates = {
            "data": plan.overage_rates.get("data_per_gb", 0),
            "voice": plan.overage_rates.get("voice_per_minute", 0),
            "sms": plan.overage_rates.get("sms_per_message", 0),
        }
        return allowances.get(usage_type, 0), rates.get(usage_type, 0)


def build_billing_from_config(config: Config) -> BillingSystem:
    billing = BillingSystem()
    for item in config.plans.get("plans", []):
        billing.add_plan(
            ServicePlan(
                plan_id=item["plan_id"],
                name=item["name"],
                description=item.get("description", ""),
                monthly_fee=Decimal(str(item["monthly_fee"])),
                data_allowance_gb=float(item.get("data_allowance_gb", 0)),
                voice_minutes=int(item.get("voice_minutes", 0)),
                sms_count=int(item.get("sms_count", 0)),
                overage_rates={
                    k: Decimal(str(v)) for k, v in item.get("overage_rates", {}).items()
                },
            )
        )
    for item in config.subscribers.get("subscribers", []):
        billing.add_subscriber(
            Subscriber(
                subscriber_id=item["subscriber_id"],
                account_number=item.get("account_number", ""),
                name=item["name"],
                phone_number=item.get("phone_number", ""),
                email=item.get("email", ""),
                address=item.get("address", {}),
                plan_id=item["plan_id"],
                status=item.get("status", "active"),
            )
        )
    return billing
