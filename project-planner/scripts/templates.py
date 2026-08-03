"""Project template library for project-planner skill."""
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Task:
    id: str
    name: str
    estimate_days: float
    phase: str
    dependencies: List[str] = field(default_factory=list)
    assignee: str = ""
    priority: str = "medium"


@dataclass
class Phase:
    name: str
    tasks: List[Task] = field(default_factory=list)
    duration_days: float = 0.0


@dataclass
class ProjectTemplate:
    name: str
    template_type: str
    description: str
    phases: List[Phase] = field(default_factory=list)
    milestones: List[str] = field(default_factory=list)
    risks: List[Dict[str, str]] = field(default_factory=list)
    resources: Dict[str, float] = field(default_factory=dict)


WEB_APP_TEMPLATE = ProjectTemplate(
    name="Web Application",
    template_type="web_app",
    description="Standard web application development project",
    phases=[
        Phase("Discovery", [
            Task("T1", "Requirements gathering", 3, "Discovery"),
            Task("T2", "Technical architecture design", 2, "Discovery"),
            Task("T3", "Stakeholder alignment", 1, "Discovery"),
        ]),
        Phase("Design", [
            Task("T4", "UI/UX wireframes", 3, "Design"),
            Task("T5", "Design system setup", 2, "Design"),
            Task("T6", "Prototype review", 1, "Design"),
        ]),
        Phase("Implementation", [
            Task("T7", "Frontend scaffold", 2, "Implementation"),
            Task("T8", "Backend API development", 5, "Implementation"),
            Task("T9", "Database schema and migrations", 2, "Implementation"),
            Task("T10", "Frontend components", 4, "Implementation"),
            Task("T11", "Integration and API wiring", 3, "Implementation"),
        ]),
        Phase("Testing", [
            Task("T12", "Unit tests", 2, "Testing"),
            Task("T13", "Integration tests", 2, "Testing"),
            Task("T14", "E2E testing", 2, "Testing"),
            Task("T15", "Performance testing", 1, "Testing"),
        ]),
        Phase("Deployment", [
            Task("T16", "CI/CD pipeline setup", 1, "Deployment"),
            Task("T17", "Staging deployment", 1, "Deployment"),
            Task("T18", "Production deployment", 1, "Deployment"),
            Task("T19", "Post-launch monitoring", 2, "Deployment"),
        ]),
    ],
    milestones=["Discovery complete", "Design approved", "MVP ready", "UAT passed", "Production live"],
    risks=[
        {"risk": "Scope creep", "likelihood": "medium", "impact": "high", "mitigation": "Strict change control process"},
        {"risk": "Technical debt accumulation", "likelihood": "medium", "impact": "medium", "mitigation": "Definition of done includes refactoring"},
        {"risk": "Stakeholder availability", "likelihood": "low", "impact": "high", "mitigation": "Scheduled check-ins with escalation path"},
    ],
    resources={"dev_hours_per_week": 40, "design_hours_per_week": 20, "qa_hours_per_week": 20},
)

API_SERVICE_TEMPLATE = ProjectTemplate(
    name="API Service",
    template_type="api_service",
    description="REST/GraphQL API service development project",
    phases=[
        Phase("Discovery", [
            Task("T1", "API requirements and contract definition", 2, "Discovery"),
            Task("T2", "Data model design", 2, "Discovery"),
            Task("T3", "Authentication/authorization design", 1, "Discovery"),
        ]),
        Phase("Implementation", [
            Task("T4", "Project scaffold and structure", 1, "Implementation"),
            Task("T5", "Core API endpoints", 4, "Implementation"),
            Task("T6", "Database layer and migrations", 2, "Implementation"),
            Task("T7", "Authentication middleware", 2, "Implementation"),
            Task("T8", "Input validation and error handling", 2, "Implementation"),
        ]),
        Phase("Testing", [
            Task("T9", "Unit tests for endpoints", 2, "Testing"),
            Task("T10", "Integration tests", 2, "Testing"),
            Task("T11", "Contract tests", 1, "Testing"),
            Task("T12", "Load testing", 1, "Testing"),
        ]),
        Phase("Deployment", [
            Task("T13", "Docker containerization", 1, "Deployment"),
            Task("T14", "CI/CD pipeline", 1, "Deployment"),
            Task("T15", "Production deployment", 1, "Deployment"),
        ]),
    ],
    milestones=["API contract finalized", "Core endpoints implemented", "Tests passing", "Deployed to production"],
    risks=[
        {"risk": "API versioning issues", "likelihood": "medium", "impact": "medium", "mitigation": "Version from day one"},
        {"risk": "Performance under load", "likelihood": "medium", "impact": "high", "mitigation": "Load testing early and often"},
    ],
    resources={"dev_hours_per_week": 40, "qa_hours_per_week": 15},
)

CLI_TOOL_TEMPLATE = ProjectTemplate(
    name="CLI Tool",
    template_type="cli_tool",
    description="Command-line tool development project",
    phases=[
        Phase("Discovery", [
            Task("T1", "Use case analysis", 1, "Discovery"),
            Task("T2", "Command structure design", 1, "Discovery"),
        ]),
        Phase("Implementation", [
            Task("T3", "Project scaffold", 1, "Implementation"),
            Task("T4", "Core commands", 3, "Implementation"),
            Task("T5", "Input parsing and validation", 2, "Implementation"),
            Task("T6", "Output formatting", 1, "Implementation"),
        ]),
        Phase("Testing", [
            Task("T7", "Unit tests", 2, "Testing"),
            Task("T8", "Integration tests", 1, "Testing"),
        ]),
        Phase("Distribution", [
            Task("T9", "Packaging (pip/Homebrew)", 1, "Distribution"),
            Task("T10", "Documentation", 1, "Distribution"),
        ]),
    ],
    milestones=["Core commands working", "Tests passing", "Packaged and distributed"],
    risks=[
        {"risk": "Cross-platform compatibility", "likelihood": "medium", "impact": "medium", "mitigation": "Test on target platforms early"},
    ],
    resources={"dev_hours_per_week": 40},
)

DATA_PIPELINE_TEMPLATE = ProjectTemplate(
    name="Data Pipeline",
    template_type="data_pipeline",
    description="ETL/data pipeline development project",
    phases=[
        Phase("Discovery", [
            Task("T1", "Source system analysis", 2, "Discovery"),
            Task("T2", "Data quality requirements", 1, "Discovery"),
            Task("T3", "Transformation rules", 2, "Discovery"),
        ]),
        Phase("Implementation", [
            Task("T4", "Ingestion connectors", 3, "Implementation"),
            Task("T5", "Transformation logic", 4, "Implementation"),
            Task("T6", "Output writers", 2, "Implementation"),
            Task("T7", "Error handling and retries", 2, "Implementation"),
        ]),
        Phase("Testing", [
            Task("T8", "Unit tests for transforms", 2, "Testing"),
            Task("T9", "Integration tests with sample data", 2, "Testing"),
            Task("T10", "Data quality validation", 1, "Testing"),
        ]),
        Phase("Deployment", [
            Task("T11", "Orchestration setup", 1, "Deployment"),
            Task("T12", "Monitoring and alerting", 1, "Deployment"),
        ]),
    ],
    milestones=["Ingestion working", "Transforms validated", "Pipeline deployed", "Monitoring active"],
    risks=[
        {"risk": "Data quality issues in source", "likelihood": "high", "impact": "high", "mitigation": "Data validation at ingestion"},
        {"risk": "Pipeline performance", "likelihood": "medium", "impact": "medium", "mitigation": "Batch processing and parallelism"},
    ],
    resources={"dev_hours_per_week": 40, "data_engineer_hours_per_week": 20},
)

ML_PROJECT_TEMPLATE = ProjectTemplate(
    name="Machine Learning Project",
    template_type="ml_project",
    description="ML model development and deployment project",
    phases=[
        Phase("Discovery", [
            Task("T1", "Problem definition and success metrics", 2, "Discovery"),
            Task("T2", "Data exploration and analysis", 3, "Discovery"),
            Task("T3", "Feature engineering plan", 2, "Discovery"),
        ]),
        Phase("Modeling", [
            Task("T4", "Baseline model", 2, "Modeling"),
            Task("T5", "Feature engineering", 3, "Modeling"),
            Task("T6", "Model training and tuning", 4, "Modeling"),
            Task("T7", "Model evaluation", 2, "Modeling"),
        ]),
        Phase("Deployment", [
            Task("T8", "Model packaging", 2, "Deployment"),
            Task("T9", "API serving setup", 2, "Deployment"),
            Task("T10", "Monitoring and drift detection", 2, "Deployment"),
        ]),
    ],
    milestones=["Baseline established", "Target metric achieved", "Model deployed", "Monitoring active"],
    risks=[
        {"risk": "Insufficient training data", "likelihood": "high", "impact": "high", "mitigation": "Data augmentation and synthetic data"},
        {"risk": "Model drift over time", "likelihood": "medium", "impact": "high", "mitigation": "Continuous monitoring and retraining pipeline"},
    ],
    resources={"dev_hours_per_week": 40, "gpu_hours_per_week": 20},
)

TEMPLATES = {
    "web_app": WEB_APP_TEMPLATE,
    "api_service": API_SERVICE_TEMPLATE,
    "cli_tool": CLI_TOOL_TEMPLATE,
    "data_pipeline": DATA_PIPELINE_TEMPLATE,
    "ml_project": ML_PROJECT_TEMPLATE,
}


def get_template(name: str) -> Optional[ProjectTemplate]:
    return TEMPLATES.get(name)


def list_templates() -> List[str]:
    return list(TEMPLATES.keys())