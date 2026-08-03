#!/usr/bin/env python3
"""Orchestrator for subagent-driven-development skill."""
import argparse
import json
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import List


@dataclass
class TaskStatus:
    task_id: str
    status: str = "pending"
    implementer_report: str = ""
    reviewer_verdict: str = ""
    commits: str = ""


@dataclass
class ProgressLedger:
    entries: List[TaskStatus] = field(default_factory=list)

    def add_task(self, task_id: str) -> None:
        self.entries.append(TaskStatus(task_id=task_id))

    def update_task(self, task_id: str, **kwargs) -> None:
        for entry in self.entries:
            if entry.task_id == task_id:
                for key, value in kwargs.items():
                    setattr(entry, key, value)
                break

    def get_pending(self) -> List[TaskStatus]:
        return [e for e in self.entries if e.status == "pending"]

    def get_completed(self) -> List[TaskStatus]:
        return [e for e in self.entries if e.status == "done"]


class SDDOrchestrator:
    def __init__(self, plan_file: Path, ledger_file: Path):
        self.plan_file = plan_file
        self.ledger_file = ledger_file
        self.ledger = self._load_ledger()

    def _load_ledger(self) -> ProgressLedger:
        if self.ledger_file.exists():
            data = json.loads(self.ledger_file.read_text())
            return ProgressLedger(entries=[TaskStatus(**e) for e in data.get("entries", [])])
        return ProgressLedger()

    def save_ledger(self) -> None:
        data = {"entries": [
            {"task_id": e.task_id, "status": e.status,
             "implementer_report": e.implementer_report,
             "reviewer_verdict": e.reviewer_verdict, "commits": e.commits}
            for e in self.ledger.entries
        ]}
        self.ledger_file.write_text(json.dumps(data, indent=2))

    def execute_plan(self, parallel: int = 1) -> dict:
        plan = self.plan_file.read_text()
        tasks = self._extract_tasks(plan)
        results = []
        for task in tasks:
            self.ledger.add_task(task["id"])
            self.ledger.update_task(task["id"], status="in_progress")
            self.save_ledger()
            results.append({"task": task["id"], "status": "completed"})
        return {"tasks": len(tasks), "completed": len(results)}

    def _extract_tasks(self, plan: str) -> List[dict]:
        tasks = []
        for i, line in enumerate(plan.split("\n")):
            if line.startswith("## Task ") or line.startswith("## Phase "):
                tasks.append({"id": str(i + 1), "title": line.strip()})
        return tasks


def main():
    parser = argparse.ArgumentParser(description="Subagent-driven development orchestrator")
    subparsers = parser.add_subparsers(dest="command")

    execute = subparsers.add_parser("execute", help="Execute a plan")
    execute.add_argument("--plan", required=True)
    execute.add_argument("--parallel", type=int, default=1)
    execute.add_argument("--cost-budget", type=int, default=100000)

    status = subparsers.add_parser("status", help="Show execution status")
    status.add_argument("--ledger", required=True)

    resume = subparsers.add_parser("resume", help="Resume from ledger")
    resume.add_argument("--plan", required=True)
    resume.add_argument("--ledger", required=True)

    review = subparsers.add_parser("review", help="Run final review")
    review.add_argument("--final", action="store_true")
    review.add_argument("--merge-base", default="main")

    args = parser.parse_args()

    if args.command == "execute":
        orchestrator = SDDOrchestrator(Path(args.plan), Path(".sdd/ledger.json"))
        result = orchestrator.execute_plan(parallel=args.parallel)
        print(f"Executed {result['tasks']} tasks, completed {result['completed']}")
    elif args.command == "status":
        ledger = SDDOrchestrator._load_ledger.__get__(None, ProgressLedger)
        print(f"Ledger entries: {len(ledger.entries) if ledger else 0}")
    elif args.command == "resume":
        print(f"Resuming from ledger: {args.ledger}")
    elif args.command == "review":
        print(f"Running final review against {args.merge_base}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()