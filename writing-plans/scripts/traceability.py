"""Plan-to-code traceability for the writing-plans skill.

Links plan tasks to git commits that touched their files and detects drift
between what a plan specifies and what the repository contains.
"""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .plans import Plan, Task


@dataclass
class TaskCommitLink:
    task_id: int
    task_title: str
    commits: list[str] = field(default_factory=list)
    referenced: int = 0
    covered: bool = False


@dataclass
class TraceabilityReport:
    links: list[TaskCommitLink] = field(default_factory=list)
    overall_coverage: float = 0.0
    unlinked_tasks: list[int] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"coverage={self.overall_coverage:.0%} "
            f"linked={len(self.links) - len(self.unlinked_tasks)}/{len(self.links)} "
            f"unlinked={self.unlinked_tasks}"
        )


class PlanTraceability:
    """Correlates plan tasks with commit history."""

    def __init__(self, project_dir: str | Path = "."):
        self.project_dir = Path(project_dir)

    def link_tasks_to_commits(self, plan: Plan) -> TraceabilityReport:
        links = []
        for task in plan.tasks:
            commits = self._commits_for_task(task)
            task_refs = [c for c in commits if str(task.number) in c]
            links.append(
                TaskCommitLink(
                    task_id=task.number,
                    task_title=task.title,
                    commits=commits,
                    referenced=len(task_refs),
                    covered=bool(commits),
                )
            )
        covered = sum(1 for link in links if link.covered)
        coverage = covered / len(links) if links else 0.0
        unlinked = [link.task_id for link in links if not link.covered]
        return TraceabilityReport(links=links, overall_coverage=round(coverage, 3), unlinked_tasks=unlinked)

    def detect_drift(self, plan: Plan) -> list[str]:
        """Return files the plan says must exist but are missing from disk."""
        missing = []
        for task in plan.tasks:
            for kind, paths in task.files.items():
                if kind in ("create", "modify"):
                    for path in paths:
                        if not (self.project_dir / path).exists():
                            missing.append(f"Task {task.number}: {path} does not exist")
        return missing

    def _commits_for_task(self, task: Task) -> list[str]:
        git = shutil.which("git")
        if git is None or not self.project_dir.joinpath(".git").exists():
            return []
        files = [p for paths in task.files.values() for p in paths]
        if not files:
            return []
        try:
            proc = subprocess.run(
                [git, "log", "--oneline", "--", *files],
                capture_output=True,
                text=True,
                cwd=self.project_dir,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired):
            return []
        if proc.returncode != 0:
            return []
        return [line.split(maxsplit=1)[0] if line.split() else line for line in proc.stdout.splitlines()]
