# Improvement Plan: telecommunications-expert

## Current State Assessment

**Tier:** 🟢 Production-Ready (Minor Polish)
**Lines:** 701 | **Version:** 1.0 (implied)

### Strengths
- Comprehensive coverage: NMS, Billing, 5G management
- Working Python implementations with dataclasses
- Real-world patterns (SNMP monitoring, alarm management, capacity planning)
- 3GPP/TM Forum/ETSI/ITU standards references
- Best practices and anti-patterns sections
- Resource links to industry bodies

### Gaps Identified
1. **No modular structure** - Single 701-line file, hard to navigate
2. **No CLI tooling** - Manual code execution only
3. **No configuration management** - Hardcoded thresholds, no config files
4. **No testing** - No unit/integration tests for the implementations
5. **No SNMP library integration** - Placeholder random values
6. **No database persistence** - In-memory only
6. **No alerting integrations** - SMS/email/page placeholders
7. **No API server** - No REST/gRPC interface
8. **No visualization** - No dashboard, charts, topology maps
9. **No multi-vendor support** - Generic implementations only
10. **No CI/CD** - No quality gates

---

## Improvement Roadmap

### Phase 1: Modularization & Config (Week 1)
- [ ] Split into modules: `nms/`, `billing/`, `fiveg/`, `core/`
- [ ] Add configuration system (YAML/JSON for thresholds, vendors)
- [ ] Create CLI entry points for each module
- [ ] Add logging and structured output

### Phase 2: Real Integrations (Week 2)
- [ ] Integrate real SNMP library (pysnmp)
- [ ] Add database persistence (SQLite/PostgreSQL)
- [ ] Implement alerting integrations (email, Slack, PagerDuty)
- [ ] Add multi-vendor device profiles (Cisco, Juniper, Huawei, Ericsson, Nokia)

### Phase 3: API & Visualization (Week 3)
- [ ] Build REST API (FastAPI) for NMS/Billing/5G
- [ ] Create web dashboard (React/Vue) with topology map
- [ ] Add real-time charts (Grafana integration)
- [ ] Implement network topology visualization

### Phase 4: Production Features (Week 4)
- [ ] Add unit/integration tests (pytest)
- [ ] Create CI/CD pipeline (GitHub Actions)
- [ ] Add configuration validation
- [ ] Create deployment guides (Docker, Kubernetes)
- [ ] Add documentation (OpenAPI, user guides)

---

## Specific Technical Tasks

### Module Structure
```
telecommunications-expert/
├── SKILL.md                 # Overview + workflows
├── config/
│   ├── thresholds.yaml      # Warning/critical thresholds per metric
│   ├── vendors.yaml         # Device profiles per vendor
│   └── alerts.yaml          # Alerting channels config
├── core/
│   ├── models.py            # Shared dataclasses (NetworkElement, Alarm, etc.)
│   ├── config.py            # Configuration loader
│   └── exceptions.py        # Custom exceptions
├── nms/
│   ├── __init__.py
│   ├── snmp_client.py       # Real SNMP integration (pysnmp)
│   ├── monitor.py           # NetworkMonitor class
│   ├── alarm_manager.py     # Alarm lifecycle
│   ├── capacity.py          # Capacity planning
│   └── cli.py               # CLI commands
├── billing/
│   ├── __init__.py
│   ├── models.py            # Subscriber, Plan, Usage, Invoice
│   ├── processor.py         # Usage processing
│   ├── invoice.py           # Invoice generation
│   └── cli.py
├── fiveg/
│   ├── __init__.py
│   ├── slice_manager.py     # Network slice management
│   ├── beamforming.py       # Massive MIMO optimization
│   ├── handover.py          # Handover management
│   └── cli.py
├── api/
│   ├── main.py              # FastAPI app
│   ├── routes/
│   │   ├── nms.py
│   │   ├── billing.py
│   │   └── fiveg.py
│   └── websocket.py         # Real-time updates
├── dashboard/
│   ├── frontend/            # React/Vue app
│   └── backend/             # Dashboard API
├── tests/
│   ├── test_nms.py
│   ├── test_billing.py
│   ├── test_fiveg.py
│   └── test_integration.py
├── scripts/
│   ├── init_db.py
│   ├── migrate_config.py
│   └── demo_data.py
└── docker/
    ├── Dockerfile
    ├── docker-compose.yml
    └── kubernetes/
```

### Configuration System
```python
# core/config.py
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ThresholdConfig:
    warning: float
    critical: float

@dataclass
class VendorProfile:
    name: str
    snmp_oids: Dict[str, str]
    default_thresholds: Dict[str, ThresholdConfig]
    cli_commands: Dict[str, str]

class Config:
    def __init__(self, config_dir: Path = Path("config")):
        self.config_dir = config_dir
        self.thresholds = self.load_yaml("thresholds.yaml")
        self.vendors = self.load_yaml("vendors.yaml")
        self.alerts = self.load_yaml("alerts.yaml")
    
    def get_threshold(self, metric: str, vendor: str = None) -> ThresholdConfig:
        # Vendor-specific > global default
        pass
```

### CLI Design
```bash
# telecom nms monitor --element NE-001 --config config/
# telecom nms alarms --severity critical --since 1h
# telecom nms capacity --region "North" --predict 12
# telecom billing process --usage-file usage.csv
# telecom billing invoice --subscriber SUB-001 --period 2026-08
# telecom fiveg slice create --name "URLLC-slice" --type urllc --latency 1
# telecom fiveg beamforming --bs BS-001 --users positions.json
# telecom api serve --host 0.0.0.0 --port 8000
```

### SNMP Integration
```python
# nms/snmp_client.py
from pysnmp.hlapi import *

class SNMPClient:
    def __init__(self, host: str, community: str = "public", port: int = 161):
        self.host = host
        self.community = community
        self.port = port
    
    def get(self, oid: str) -> Any:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.host, self.port)),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        if errorIndication:
            raise SNMPError(errorIndication)
        return varBinds[0][1]
    
    def walk(self, oid: str) -> List[Any]:
        # bulk walk implementation
        pass
```

---

## Acceptance Criteria
- [ ] Modular structure with clear separation of concerns
- [ ] Real SNMP integration works with test devices
- [ ] Database persistence for all entities
- [ ] REST API responds in <100ms for standard queries
- [ ] Dashboard shows real-time topology and metrics
- [ ] Alerting sends notifications via configured channels
- [ ] Unit tests cover >80% of business logic
- [ ] CI/CD passes on every commit
- [ ] Docker deployment works locally and in K8s

---

## Dependencies
- `code-quality` (script validation)
- `fastapi-expert` (API design)
- `test-driven-development` (test approach)
- `verification-before-completion` (quality claims)
- `devops-engineer` (deployment)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SNMP library complexity | Medium | High | Start with basic GET, add WALK later |
| Vendor OID differences | High | Medium | Configurable OID mappings per vendor |
| Real-time dashboard performance | Medium | Medium | WebSocket + efficient queries |
| Data model migration | Low | High | Alembic migrations, versioned schema |

---

## Success Metrics
- Module imports: <1s each
- SNMP query latency: <500ms
- API response time: <100ms p95
- Test coverage: >80%
- Deployment time: <5 min
- Multi-vendor support: 5+ vendors