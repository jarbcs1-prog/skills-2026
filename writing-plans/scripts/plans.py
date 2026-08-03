"""Plan document model and markdown parser for the writing-plans skill.

A plan is a markdown document with a header block and one or more tasks.
Tasks carry an objective, the files they create/modify, a status and ordered
steps. The parser round-trips this format so plans can be generated,
validated, composed, versioned and tracked.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PlanStep:
    """A single actionable step inside a task."""

    title: str
    content: str = ""


@dataclass
class Task:
    """A bite-sized (2-5 minute) unit of implementation work."""

    number: int
    title: str
    objective: str = ""
    files: dict[str, list[str]] = field(default_factory=dict)
    status: str = "pending"
    steps: list[PlanStep] = field(default_factory=list)
    raw: str = ""

    def creates_code(self) -> bool:
        """True when the task creates or modifies a source file."""
        return bool(self.files.get("create") or self.files.get("modify"))

    def has_tdd_cycle(self) -> bool:
        titles = [s.title.lower() for s in self.steps]
        return any("test" in t for t in titles) and any("implement" in t for t in titles)


@dataclass
class PlanHeader:
    """Metadata block at the top of a plan document."""

    name: str = ""
    goal: str = ""
    architecture: str = ""
    tech_stack: str = ""
    version: str = "0.1.0"


@dataclass
class Plan:
    """A complete implementation plan document."""

    header: PlanHeader = field(default_factory=PlanHeader)
    tasks: list[Task] = field(default_factory=list)
    path: Path | None = None
    raw: str = ""

    def task_by_number(self, number: int) -> Task | None:
        for task in self.tasks:
            if task.number == number:
                return task
        return None


_STATUSES = ("pending", "in_progress", "done", "blocked", "cancelled")


def render_plan(plan: Plan) -> str:
    """Serialize a Plan object back to markdown."""
    header = plan.header
    lines = [f"# {header.name} Implementation Plan", ""]
    if header.goal:
        lines += [f"**Goal:** {header.goal}", ""]
    if header.architecture:
        lines += [f"**Architecture:** {header.architecture}", ""]
    if header.tech_stack:
        lines += [f"**Tech Stack:** {header.tech_stack}", ""]
    lines += [f"**Version:** {header.version}", "", "---", ""]
    for task in plan.tasks:
        lines += [f"## Task {task.number}: {task.title}", ""]
        lines += [f"**Status:** {task.status}", ""]
        if task.objective:
            lines += [f"**Objective:** {task.objective}", ""]
        if task.files:
            lines.append("**Files:**")
            for kind, paths in task.files.items():
                for path in paths:
                    lines.append(f"- {kind}: `{path}`")
            lines.append("")
        for step in task.steps:
            lines += [f"**Step {step.title}**", "", step.content.strip(), ""]
    return "\n".join(lines).rstrip() + "\n"


def parse_plan(text: str) -> Plan:
    """Parse plan markdown into a Plan object."""
    plan = Plan(raw=text)
    title_match = re.search(r"^#\s+(.+?)\s+Implementation\s+Plan\s*$", text, re.MULTILINE)
    if title_match:
        plan.header.name = title_match.group(1).strip()

    def _grab(label: str) -> str:
        match = re.search(rf"^\*\*{label}:\*\*\s*(.+)$", text, re.MULTILINE)
        return match.group(1).strip() if match else ""

    plan.header.goal = _grab("Goal")
    plan.header.architecture = _grab("Architecture")
    plan.header.tech_stack = _grab("Tech Stack")
    version_match = re.search(r"^\*\*Version:\*\*\s*([\w.\-]+)", text, re.MULTILINE)
    if version_match:
        plan.header.version = version_match.group(1).strip()

    task_blocks = re.split(r"(?m)^## Task\s+", text)
    for block in task_blocks[1:]:
        plan.tasks.append(_parse_task_block(block))
    return plan


def _parse_task_block(block: str) -> Task:
    lines = block.splitlines()
    first = lines[0].strip() if lines else ""
    number_match = re.match(r"^(\d+):\s*(.+)$", first)
    number = int(number_match.group(1)) if number_match else 0
    title = number_match.group(2).strip() if number_match else first
    task = Task(number=number, title=title, raw=block)
    for line in lines[1:]:
        status_match = re.match(r"^\*\*Status:\*\*\s*(.+)$", line.strip())
        if status_match:
            task.status = status_match.group(1).strip().lower()
            continue
        obj_match = re.match(r"^\*\*Objective:\*\*\s*(.+)$", line.strip())
        if obj_match:
            task.objective = obj_match.group(1).strip()
            continue
        file_match = re.match(r"^-\s*(Create|Modify|Test|Delete|Move|Reference):\s*`([^`]+)`", line.strip())
        if file_match:
            kind = file_match.group(1).lower()
            task.files.setdefault(kind, []).append(file_match.group(2).strip())
            continue
        step_match = re.match(r"^\*\*Step\s+(.+?)\*\*", line.strip())
        if step_match:
            task.steps.append(PlanStep(title=step_match.group(1).strip()))
            continue
        if task.steps:
            task.steps[-1].content = (task.steps[-1].content + "\n" + line).strip()
    return task


def save_plan(plan: Plan, path: str | Path) -> Path:
    """Write a plan document to disk and return its path."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_plan(plan), encoding="utf-8")
    plan.path = target
    return target


def load_plan(path: str | Path) -> Plan:
    """Load a plan document from disk."""
    target = Path(path)
    plan = parse_plan(target.read_text(encoding="utf-8"))
    plan.path = target
    return plan
