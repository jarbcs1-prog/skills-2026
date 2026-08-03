from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path


from billing.invoice import InvoiceGenerator
from billing.models import ServicePlan, Subscriber, UsageRecord
from billing.processor import BillingSystem, build_billing_from_config
from core.config import Config

SKILL_ROOT = Path(__file__).parent.parent


def _billing_system() -> BillingSystem:
    billing = BillingSystem()
    billing.add_plan(
        ServicePlan(
            plan_id="PLAN-BASIC",
            name="Basic",
            description="Entry-level bundle",
            monthly_fee=Decimal("29.99"),
            data_allowance_gb=10.0,
            voice_minutes=300,
            sms_count=100,
            overage_rates={
                "data_per_gb": Decimal("5.00"),
                "voice_per_minute": Decimal("0.10"),
                "sms_per_message": Decimal("0.05"),
            },
        )
    )
    billing.add_subscriber(
        Subscriber(
            subscriber_id="SUB-001",
            account_number="ACC-0001",
            name="Jane Doe",
            phone_number="+1-555-0101",
            email="jane@example.com",
            plan_id="PLAN-BASIC",
        )
    )
    billing.add_subscriber(
        Subscriber(
            subscriber_id="SUB-002",
            account_number="ACC-0002",
            name="Suspended",
            phone_number="+1-555-0102",
            email="s@example.com",
            plan_id="PLAN-BASIC",
            status="suspended",
        )
    )
    return billing


def _usage(record_id: str, subscriber: str, usage_type: str, quantity: float) -> UsageRecord:
    return UsageRecord(
        record_id=record_id,
        subscriber_id=subscriber,
        usage_type=usage_type,
        timestamp=datetime.now(),
        quantity=quantity,
        unit="GB" if usage_type == "data" else "minutes",
    )


def test_process_usage_unknown_subscriber():
    result = _billing_system().process_usage(_usage("R1", "NOPE", "data", 1.0))
    assert result["error"] == "Subscriber not found"


def test_process_usage_suspended_subscriber():
    result = _billing_system().process_usage(_usage("R1", "SUB-002", "data", 1.0))
    assert result["error"] == "Subscriber not active"


def test_process_usage_within_allowance():
    billing = _billing_system()
    result = billing.process_usage(_usage("R1", "SUB-001", "data", 5.0))
    assert result["charge"] == 0.0
    assert result["within_allowance"] is True


def test_process_usage_overage():
    billing = _billing_system()
    billing.process_usage(_usage("R1", "SUB-001", "data", 6.0))
    billing.process_usage(_usage("R2", "SUB-001", "data", 6.0))
    result = billing.process_usage(_usage("R3", "SUB-001", "data", 6.0))
    assert result["within_allowance"] is False
    assert result["charge"] == 30.0


def test_build_billing_from_config():
    billing = build_billing_from_config(Config(SKILL_ROOT / "config"))
    assert set(billing.service_plans) == {"PLAN-BASIC", "PLAN-UNLIMITED"}
    assert set(billing.subscribers) == {"SUB-001", "SUB-002", "SUB-003"}
    assert billing.subscribers["SUB-003"].status == "suspended"


def test_invoice_totals():
    billing = _billing_system()
    now = datetime.now()
    for i in range(25):
        billing.usage_records.append(
            UsageRecord(
                record_id=f"U{i}",
                subscriber_id="SUB-001",
                usage_type="data",
                timestamp=now,
                quantity=1.0,
                unit="GB",
            )
        )
    invoice = InvoiceGenerator(billing).generate_invoice(
        "SUB-001", (now.replace(day=1), now)
    )
    assert invoice["monthly_fee"] == 29.99
    assert invoice["usage_charges"]["data"] == 75.0
    assert invoice["subtotal"] == 104.99
    assert invoice["taxes"] == 10.499
    assert invoice["total"] == 115.489
    assert invoice["invoice_id"].startswith("INV-")
    assert billing.invoices == [invoice]


def test_invoice_unknown_subscriber():
    invoice = InvoiceGenerator(_billing_system()).generate_invoice(
        "NOPE", (datetime.now(), datetime.now())
    )
    assert invoice["error"] == "Subscriber not found"
