"""Plan validator for the writing-plans skill.

Checks structure, TDD compliance, granularity, completeness and traceability.
Returns errors, warnings and a 0-100 score. Errors indicate an invalid plan;
warnings indicate quality issues.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .plans import Plan, Task

_ERROR_WEIGHT = 5
_WARNING_WEIGHT = 1


@dataclass
class ValidationResult:
    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    score: int = 100

    def summary(self) -> str:
        return (
            f"valid={self.valid} score={self.score}/100 "
            f"errors={len(self.errors)} warnings={len(self.warnings)}"
        )


class PlanValidator:
    """Runs structural and quality checks against a Plan."""

    def validate(self, plan: Plan, strict: bool = False) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        errors += self._validate_header(plan)
        if not plan.tasks:
            errors.append("Plan has no tasks")

        for task in plan.tasks:
            errors += self._validate_task_structure(task)
            warnings += self._check_tdd_compliance(task)
            warnings += self._check_granularity(task)
            warnings += self._check_step_verification(task)

        score = 100
        score -= len(errors) * _ERROR_WEIGHT
        score -= len(warnings) * _WARNING_WEIGHT
        score = max(0, min(100, score))

        valid = not errors
        if strict and score < 70:
            valid = False
        return ValidationResult(valid=valid, errors=errors, warnings=warnings, score=score)

    @staticmethod
    def _validate_header(plan: Plan) -> list[str]:
        errors = []
        if not plan.header.name:
            errors.append("Header missing: plan name (expected '# <Name> Implementation Plan')")
        if not plan.header.goal:
            errors.append("Header missing: Goal")
        if not plan.header.architecture:
            errors.append("Header missing: Architecture")
        if not plan.header.tech_stack:
            errors.append("Header missing: Tech Stack")
        return errors

    @staticmethod
    def _validate_task_structure(task: Task) -> list[str]:
        errors = []
        if not task.title:
            errors.append(f"Task {task.number}: missing title")
        if not task.objective:
            errors.append(f"Task {task.number}: missing Objective")
        if not task.steps:
            errors.append(f"Task {task.number}: no steps defined")
        return errors

    @staticmethod
    def _check_tdd_compliance(task: Task) -> list[str]:
        warnings = []
        if not task.creates_code():
            return warnings
        titles = [s.title.lower() for s in task.steps]
        if not any("test" in t for t in titles):
            warnings.append(f"Task {task.number}: produces code but has no test step")
        if not any("implement" in t or "write" in t for t in titles):
            warnings.append(f"Task {task.number}: produces code but has no implementation step")
        return warnings

    @staticmethod
    def _check_granularity(task: Task) -> list[str]:
        warnings = []
        created = task.files.get("create", [])
        if len(created) > 3:
            warnings.append(f"Task {task.number}: creates {len(created)} files, consider splitting")
        estimated = sum(len(step.content.splitlines()) for step in task.steps)
        if estimated > 120:
            warnings.append(f"Task {task.number}: large task (~{estimated} lines of step content), consider splitting")
        return warnings

    @staticmethod
    def _check_step_verification(task: Task) -> list[str]:
        warnings = []
        for step in task.steps:
            if "run" in step.title.lower() or "verify" in step.title.lower():
                if "expected" not in step.content.lower() and ":" not in step.title.lower():
                    warnings.append(f"Task {task.number} step '{step.title}': verification step without expected outcome")
        return warnings
