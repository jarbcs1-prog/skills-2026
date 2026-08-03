---
name: telecommunications-expert
description: Expert-level telecommunications systems, network management, billing, 5G, SDN and telecom infrastructure.
---

# Telecommunications Expert

Expert guidance for telecommunications systems, network management, billing systems, 5G networks, SDN/NFV and telecom infrastructure management.

## Core Concepts

### Telecommunications Systems
- Operations Support Systems (OSS)
- Business Support Systems (BSS)
- Network Management Systems (NMS)
- Service Assurance
- Inventory Management
- Provisioning systems
- Customer care platforms

### Network Technologies
- 5G/4G/LTE networks
- Fiber optic networks
- Software-Defined Networking (SDN)
- Network Functions Virtualization (NFV)
- Edge computing
- IoT connectivity
- Satellite communications

### Standards and Protocols
- 3GPP standards
- TM Forum Frameworx
- ETSI specifications
- ITU-T recommendations
- SIP (Session Initiation Protocol)
- Diameter protocol
- SNMP for network management

## Module Reference

The package ships a runnable reference implementation under `F:\skills_2026\telecommunications-expert`. Python 3.10+ only; no third-party runtime dependencies (YAML config loading uses PyYAML; SNMP, FastAPI and uvicorn are optional and lazily imported).

```
telecommunications-expert/
├── config/            # YAML configuration: thresholds, vendors, alerts, elements, subscribers, plans
├── core/              # Shared domain: config loader, models (NetworkElement/NetworkAlarm/...), exceptions
├── nms/               # Network Management System: monitoring, alarms, capacity planning, SNMP client
├── billing/           # BSS: subscribers, plans, usage mediation, invoice generation
├── fiveg/             # 5G: network slicing, beamforming, handover management
├── api/               # Optional FastAPI/uvicorn HTTP server
├── scripts/           # `telecom` CLI (run via `python -m scripts.cli`)
└── tests/             # pytest suite (43 tests)
```

### core
- `core.config.Config` — loads `config/*.yaml`; `get_threshold(metric, vendor)` returns a `ThresholdConfig(warning, critical)`, `get_vendor_profile(vendor)` returns `None` for unknown vendors.
- `core.models` — dataclasses `NetworkElement` (status defaults to `active`), `NetworkAlarm`, `PerformanceMetric` plus enums `AlarmSeverity`, `NetworkElementType`.
- `core.exceptions` — `TelecomError` base with `ConfigurationError`, `ElementNotFoundError`, `SubscriberNotFoundError`, `SNMPError`.

### nms
- `nms.monitor.NetworkManagementSystem` — `add_element`, `get_element` (raises `ElementNotFoundError`), `monitor_network_element(element_id)` returns a `MonitorResult` dict (`element_id`, `status`, `metrics`, `violations`, `health_score`). Health = `100 − 20·critical − 10·warning`, `0.0` when the element is not `active`. Critical violations raise alarms (`ALM-<hex10>`). Build from config with `build_nms_from_config(config)`.
- `nms.capacity` — `analyze_network_capacity(elements, region)` computes regional utilization and `predict_capacity_exhaustion(total, current, growth_rate)` (exponential, 15% annual default) returning months to 90% utilization; `expansion_recommended` when < 12 months.
- `nms.alarm_manager.AlarmManager` — `list_alarms(severity, since)`, `acknowledge`, `clear`, `active_alarms`; `parse_since('30m'|'1h'|'7d')` helper.
- `nms.snmp_client.SNMPClient` — lazy `pysnmp` wrapper (`get(oid)`, `walk(oid)`); raises `SNMPError` when pysnmp is absent.

### billing
- `billing.processor.BillingSystem` — `process_usage(usage)` returns `{'subscriber_id', 'usage_type', 'quantity', 'charge', 'within_allowance'}`; overage applies only when the month-to-date usage (before this record) exceeds the plan allowance. `build_billing_from_config(config)` wires plans + subscribers.
- `billing.invoice.InvoiceGenerator.generate_invoice(subscriber_id, billing_period)` — monthly fee + usage charges, 10% tax, due date +15 days, returns `INV-<hex10>` invoice dict.
- Errors are returned as `{'error': '...'}` dicts, never raised, for `process_usage`/`generate_invoice`.

### fiveg
- `fiveg.slice_manager.SliceManager.configure_network_slice` — validates slice type (`eMBB`/`URLLC`/`mMTC`), returns `{'slice_id': 'SLICE-<hex8>', 'status': 'configured', 'resources_allocated': True}` or `{'error': ...}` for unknown types.
- `fiveg.beamforming.BeamformingOptimizer.optimize_beamforming(bs_id, user_positions)` — 64 antennas, beam directions from `atan2`, 2.5× throughput estimate.
- `fiveg.handover.HandoverManager.manage_handover(ue_id, source, target)` — triggers handover when `target_rsrp > source_rsrp + 3dB`.

### api
- `api.server.build_app()` returns a FastAPI app (health, nms/billing/fiveg stubs); `serve(host, port)` runs it via uvicorn. Both lazy-import fastapi/uvicorn.

## CLI

Run from the skill root: `python -m scripts.cli <command> [options]`. JSON output on stdout; exit code 1 on domain errors.

```
telecom nms monitor --element NE-001 [--config config]
telecom nms alarms [--severity critical|major|minor|warning] [--since 30m|1h|24h|7d]
telecom nms capacity --region North [--predict 12] [--config config]
telecom billing process --usage-file usage.csv [--config config]
telecom billing invoice --subscriber SUB-001 --period 2026-08 [--config config]
telecom fiveg slice create --name VoLTE --type urllc [--bandwidth 100] [--latency 10] [--reliability 99.9]
telecom fiveg beamforming --bs BS-001 --users positions.json
telecom fiveg handover --ue UE-001 --source Cell-A --target Cell-B
telecom api serve [--host 0.0.0.0] [--port 8000]
```

`billing process` reads a CSV with columns `record_id,subscriber_id,usage_type,timestamp,quantity,unit`. `fiveg beamforming` reads JSON user positions as `[[x, y], ...]` or `[{"x": .., "y": ..}, ...]`.

## Best Practices

### Network Management
- Implement proactive monitoring
- Use predictive analytics for fault detection
- Automate routine tasks
- Maintain network documentation
- Implement configuration management
- Use centralized logging
- Monitor key performance indicators (KPIs)

### Billing Systems
- Ensure real-time charging
- Implement usage mediation
- Support multiple rating models
- Provide transparent billing
- Enable self-service portal
- Automate invoice generation
- Implement payment processing

### 5G Networks
- Implement network slicing
- Optimize for low latency
- Use edge computing
- Enable dynamic resource allocation
- Support massive IoT connectivity
- Implement security measures
- Monitor QoS metrics

### Service Assurance
- Track service level agreements (SLAs)
- Implement automated testing
- Monitor customer experience
- Provide real-time diagnostics
- Enable root cause analysis
- Track mean time to repair (MTTR)
- Implement service quality metrics

## Anti-Patterns

❌ Reactive network management only
❌ Manual provisioning processes
❌ No capacity planning
❌ Inaccurate billing
❌ Poor alarm management (alarm storms)
❌ No network redundancy
❌ Ignoring customer experience metrics
❌ Manual configuration changes
❌ No disaster recovery plan

## Resources

- TM Forum: https://www.tmforum.org/
- 3GPP: https://www.3gpp.org/
- ETSI: https://www.etsi.org/
- ITU-T: https://www.itu.int/
- GSMA: https://www.gsma.com/
- ONF (Open Networking Foundation): https://opennetworking.org/
- O-RAN Alliance: https://www.o-ran.org/
