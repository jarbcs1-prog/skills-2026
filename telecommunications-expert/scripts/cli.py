"""Telecom expert CLI (prog='telecom').

Usage: python -m scripts.cli <nms|billing|fiveg|api> <action> [options]
"""

from __future__ import annotations

import argparse
import calendar
import csv
import json
from datetime import datetime
from pathlib import Path

from api.server import serve
from billing.invoice import InvoiceGenerator
from billing.processor import build_billing_from_config
from billing.models import UsageRecord
from core.config import Config
from core.models import AlarmSeverity
from fiveg.beamforming import BeamformingOptimizer
from fiveg.handover import HandoverManager
from fiveg.slice_manager import SliceManager
from nms.alarm_manager import AlarmManager, parse_since
from nms.capacity import analyze_network_capacity
from nms.monitor import build_nms_from_config


def _load_config(config_dir: str) -> Config:
    return Config(Path(config_dir))


def _cmd_nms_monitor(args: argparse.Namespace) -> int:
    nms = build_nms_from_config(_load_config(args.config))
    result = nms.monitor_network_element(args.element)
    print(json.dumps(result, indent=2, default=str))
    return 0 if "error" not in result else 1


def _cmd_nms_alarms(args: argparse.Namespace) -> int:
    nms = build_nms_from_config(_load_config(args.config))
    for element_id in list(nms.network_elements):
        nms.monitor_network_element(element_id)
    manager = AlarmManager(nms.alarms)
    severity = AlarmSeverity(args.severity) if args.severity else None
    since = parse_since(args.since) if args.since else None
    filtered = manager.list_alarms(severity, since)
    print(
        json.dumps(
            {
                "alarms": [
                    {
                        "alarm_id": a.alarm_id,
                        "element_id": a.element_id,
                        "severity": a.severity,
                        "description": a.description,
                        "timestamp": a.timestamp.isoformat(),
                        "acknowledged": a.acknowledged,
                        "cleared": a.cleared,
                    }
                    for a in filtered
                ]
            },
            indent=2,
            default=str,
        )
    )
    return 0


def _cmd_nms_capacity(args: argparse.Namespace) -> int:
    nms = build_nms_from_config(_load_config(args.config))
    result = analyze_network_capacity(nms.network_elements, args.region)
    print(json.dumps(result, indent=2, default=str))
    return 0 if "error" not in result else 1


def _cmd_billing_process(args: argparse.Namespace) -> int:
    usage_file = Path(args.usage_file)
    if not usage_file.exists():
        print(f"ERROR: usage file {usage_file} not found")
        return 1
    billing = build_billing_from_config(_load_config(args.config))
    results = []
    with usage_file.open("r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            usage = UsageRecord(
                record_id=row["record_id"],
                subscriber_id=row["subscriber_id"],
                usage_type=row["usage_type"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                quantity=float(row["quantity"]),
                unit=row["unit"],
            )
            results.append(billing.process_usage(usage))
    print(json.dumps(results, indent=2, default=str))
    return 0


def _parse_period(spec: str) -> tuple:
    try:
        year, month = (int(part) for part in spec.split("-"))
    except ValueError as exc:
        raise ValueError(f"invalid period {spec!r}; expected YYYY-MM") from exc
    last_day = calendar.monthrange(year, month)[1]
    return datetime(year, month, 1), datetime(year, month, last_day)


def _cmd_billing_invoice(args: argparse.Namespace) -> int:
    billing = build_billing_from_config(_load_config(args.config))
    period = _parse_period(args.period)
    invoice = InvoiceGenerator(billing).generate_invoice(args.subscriber, period)
    print(json.dumps(invoice, indent=2, default=str))
    return 0 if "error" not in invoice else 1


def _cmd_fiveg_slice(args: argparse.Namespace) -> int:
    result = SliceManager().configure_network_slice(
        {
            "name": args.name,
            "slice_type": args.type.upper(),
            "bandwidth": args.bandwidth,
            "max_latency": args.latency,
            "reliability": args.reliability,
        }
    )
    print(json.dumps(result, indent=2, default=str))
    return 0 if "error" not in result else 1


def _load_positions(users_file: str) -> list:
    path = Path(users_file)
    if not path.exists():
        raise FileNotFoundError(f"users file {path} not found")
    return json.loads(path.read_text(encoding="utf-8"))


def _cmd_fiveg_beamforming(args: argparse.Namespace) -> int:
    try:
        positions = _load_positions(args.users)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 1
    result = BeamformingOptimizer().optimize_beamforming(args.bs, positions)
    print(json.dumps(result, indent=2, default=str))
    return 0


def _cmd_fiveg_handover(args: argparse.Namespace) -> int:
    result = HandoverManager().manage_handover(args.ue, args.source, args.target)
    print(json.dumps(result, indent=2, default=str))
    return 0


def _cmd_api_serve(args: argparse.Namespace) -> int:
    try:
        serve(host=args.host, port=args.port)
    except ImportError as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="telecom")
    subparsers = parser.add_subparsers(dest="action", required=True)

    nms = subparsers.add_parser("nms", help="network management system")
    nms_sub = nms.add_subparsers(dest="nms_action", required=True)
    monitor = nms_sub.add_parser("monitor", help="monitor a network element")
    monitor.add_argument("--element", required=True)
    monitor.add_argument("--config", default="config")
    monitor.set_defaults(func=_cmd_nms_monitor)

    alarms = nms_sub.add_parser("alarms", help="list alarms")
    alarms.add_argument("--severity", choices=["critical", "major", "minor", "warning"])
    alarms.add_argument("--since")
    alarms.add_argument("--config", default="config")
    alarms.set_defaults(func=_cmd_nms_alarms)

    capacity = nms_sub.add_parser("capacity", help="analyze regional capacity")
    capacity.add_argument("--region", required=True)
    capacity.add_argument("--predict", type=int)
    capacity.add_argument("--config", default="config")
    capacity.set_defaults(func=_cmd_nms_capacity)

    billing = subparsers.add_parser("billing", help="billing system")
    billing_sub = billing.add_subparsers(dest="billing_action", required=True)
    process = billing_sub.add_parser("process", help="process a usage file")
    process.add_argument("--usage-file", required=True)
    process.add_argument("--config", default="config")
    process.set_defaults(func=_cmd_billing_process)

    invoice = billing_sub.add_parser("invoice", help="generate an invoice")
    invoice.add_argument("--subscriber", required=True)
    invoice.add_argument("--period", required=True, help="YYYY-MM")
    invoice.add_argument("--config", default="config")
    invoice.set_defaults(func=_cmd_billing_invoice)

    fiveg = subparsers.add_parser("fiveg", help="5G network management")
    fiveg_sub = fiveg.add_subparsers(dest="fiveg_action", required=True)
    slice_cmd = fiveg_sub.add_parser("slice", help="manage network slices")
    slice_sub = slice_cmd.add_subparsers(dest="slice_action", required=True)
    create = slice_sub.add_parser("create", help="create a slice")
    create.add_argument("--name", required=True)
    create.add_argument("--type", required=True)
    create.add_argument("--bandwidth", type=int, default=100)
    create.add_argument("--latency", type=int, default=10)
    create.add_argument("--reliability", type=float, default=99.9)
    create.set_defaults(func=_cmd_fiveg_slice)

    beamforming = fiveg_sub.add_parser("beamforming", help="optimize beam directions")
    beamforming.add_argument("--bs", required=True)
    beamforming.add_argument("--users", required=True)
    beamforming.set_defaults(func=_cmd_fiveg_beamforming)

    handover = fiveg_sub.add_parser("handover", help="manage a handover")
    handover.add_argument("--ue", required=True)
    handover.add_argument("--source", required=True)
    handover.add_argument("--target", required=True)
    handover.set_defaults(func=_cmd_fiveg_handover)

    api = subparsers.add_parser("api", help="REST API")
    api_sub = api.add_subparsers(dest="api_action", required=True)
    serve_cmd = api_sub.add_parser("serve", help="run the API server")
    serve_cmd.add_argument("--host", default="0.0.0.0")
    serve_cmd.add_argument("--port", type=int, default=8000)
    serve_cmd.set_defaults(func=_cmd_api_serve)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if hasattr(args, "func"):
        return args.func(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
