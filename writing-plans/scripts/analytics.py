"""Plan analytics for the writing-plans skill.

Computes a quality report for a single plan: task counts, TDD compliance,
granularity, completeness, traceability, and an effort estimate.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .plans import Plan
from .validator import PlanValidator


@dataclass
class QualityReport:
    task_count: int = 0
    tdd_compliant_tasks: int = 0
    tdd_compliance_rate: float = 0.0
    avg_files_per_task: float = 0.0
    avg_steps_per_task: float = 0.0
    pending_tasks: int = 0
    done_tasks: int = 0
    validation_score: int = 100
    validation_errors: int = 0
    validation_warnings: int = 0
    estimated_hours: float = 0.0
    risk_factors: list[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"tasks={self.task_count} tdd={self.tdd_compliance_rate:.0%} "
            f"score={self.validation_score}/100 est_hours={self.estimated_hours:.1f}"
        )


class PlanAnalytics:
    """Evaluates plan quality and estimates effort."""

    MINUTES_PER_TASK = 5
    HOURS_PER_TASK = 0.25

    def analyze_plan_quality(self, plan: Plan) -> QualityReport:
        report = QualityReport(task_count=len(plan.tasks))
        if not plan.tasks:
            report.risk_factors.append("Plan has no tasks")
            return report

        report.tdd_compliant_tasks = sum(1 for t in plan.tasks if t.has_tdd_cycle() or not t.creates_code())
        report.tdd_compliance_rate = round(report.tdd_compliant_tasks / len(plan.tasks), 3)
        report.avg_files_per_task = round(sum(len(t.files) for t in plan.tasks) / len(plan.tasks), 2)
        report.avg_steps_per_task = round(sum(len(t.steps) for t in plan.tasks) / len(plan.tasks), 2)
        report.pending_tasks = sum(1 for t in plan.tasks if t.status in ("pending", "in_progress"))
        report.done_tasks = sum(1 for t in plan.tasks if t.status == "done")

        validation = PlanValidator().validate(plan)
        report.validation_score = validation.score
        report.validation_errors = len(validation.errors)
        report.validation_warnings = len(validation.warnings)

        report.estimated_hours = round(len(plan.tasks) * self.HOURS_PER_TASK, 1)
        if len(plan.tasks) > 15:
            report.risk_factors.append(f"{len(plan.tasks)} tasks exceeds the 15-task comfort zone")
        if validation.errors:
            report.risk_factors.append(f"{len(validation.errors)} validation errors")
        if report.pending_tasks and report.done_tasks and report.pending_tasks < report.done_tasks:
            report.risk_factors.append("More tasks done than pending - check status accuracy")
        return report
