"""Tests for subagent-driven-development orchestrator."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.orchestrator import SDDOrchestrator, ProgressLedger


def test_orchestrator_loads_ledger(tmp_path):
    ledger_file = tmp_path / "ledger.json"
    ledger_file.write_text(json.dumps({"entries": []}))
    orchestrator = SDDOrchestrator(Path("plan.md"), ledger_file)
    ledger = orchestrator._load_ledger()
    assert len(ledger.entries) == 0


def test_orchestrator_creates_ledger(tmp_path):
    ledger_file = tmp_path / "ledger.json"
    orchestrator = SDDOrchestrator(Path("plan.md"), ledger_file)
    assert len(orchestrator.ledger.entries) == 0


def test_orchestrator_adds_task():
    ledger = ProgressLedger()
    ledger.add_task("task-1")
    assert len(ledger.entries) == 1
    assert ledger.entries[0].task_id == "task-1"


def test_orchestrator_updates_task():
    ledger = ProgressLedger()
    ledger.add_task("task-1")
    ledger.update_task("task-1", status="done")
    assert ledger.entries[0].status == "done"


def test_orchestrator_get_pending():
    ledger = ProgressLedger()
    ledger.add_task("task-1")
    ledger.add_task("task-2")
    ledger.update_task("task-1", status="done")
    pending = ledger.get_pending()
    assert len(pending) == 1
    assert pending[0].task_id == "task-2"


def test_orchestrator_get_completed():
    ledger = ProgressLedger()
    ledger.add_task("task-1")
    ledger.add_task("task-2")
    ledger.update_task("task-1", status="done")
    completed = ledger.get_completed()
    assert len(completed) == 1
    assert completed[0].task_id == "task-1"


def test_orchestrator_save_ledger(tmp_path):
    ledger_file = tmp_path / "ledger.json"
    ledger = ProgressLedger()
    ledger.add_task("task-1")
    ledger.update_task("task-1", status="done")
    orchestrator = SDDOrchestrator(Path("plan.md"), ledger_file)
    orchestrator.ledger = ledger
    orchestrator.save_ledger()
    assert ledger_file.exists()
    data = json.loads(ledger_file.read_text())
    assert len(data["entries"]) == 1


def test_orchestrator_execute_plan(tmp_path):
    plan_file = tmp_path / "plan.md"
    plan_file.write_text("## Task 1: Implement feature\n\nDo the work.\n")
    ledger_file = tmp_path / "ledger.json"
    orchestrator = SDDOrchestrator(plan_file, ledger_file)
    result = orchestrator.execute_plan()
    assert result["tasks"] >= 1
    assert result["completed"] >= 0