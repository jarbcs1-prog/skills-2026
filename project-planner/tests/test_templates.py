"""Tests for project-planner templates."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.templates import (
    WEB_APP_TEMPLATE, API_SERVICE_TEMPLATE, CLI_TOOL_TEMPLATE,
    DATA_PIPELINE_TEMPLATE, ML_PROJECT_TEMPLATE, TEMPLATES,
    get_template, list_templates,
)


def test_web_app_template_has_all_fields():
    assert WEB_APP_TEMPLATE.name
    assert WEB_APP_TEMPLATE.template_type == "web_app"
    assert len(WEB_APP_TEMPLATE.phases) > 0
    assert len(WEB_APP_TEMPLATE.milestones) > 0
    assert len(WEB_APP_TEMPLATE.risks) > 0


def test_api_service_template_has_all_fields():
    assert API_SERVICE_TEMPLATE.name
    assert API_SERVICE_TEMPLATE.template_type == "api_service"
    assert len(API_SERVICE_TEMPLATE.phases) > 0


def test_cli_tool_template_has_all_fields():
    assert CLI_TOOL_TEMPLATE.name
    assert CLI_TOOL_TEMPLATE.template_type == "cli_tool"
    assert len(CLI_TOOL_TEMPLATE.phases) > 0


def test_data_pipeline_template_has_all_fields():
    assert DATA_PIPELINE_TEMPLATE.name
    assert DATA_PIPELINE_TEMPLATE.template_type == "data_pipeline"
    assert len(DATA_PIPELINE_TEMPLATE.phases) > 0


def test_ml_project_template_has_all_fields():
    assert ML_PROJECT_TEMPLATE.name
    assert ML_PROJECT_TEMPLATE.template_type == "ml_project"
    assert len(ML_PROJECT_TEMPLATE.phases) > 0


def test_all_templates_have_phases():
    for template in TEMPLATES.values():
        assert len(template.phases) > 0, f"{template.template_type} missing phases"


def test_all_templates_have_milestones():
    for template in TEMPLATES.values():
        assert len(template.milestones) > 0, f"{template.template_type} missing milestones"


def test_all_templates_have_risks():
    for template in TEMPLATES.values():
        assert len(template.risks) > 0, f"{template.template_type} missing risks"


def test_get_template_returns_correct_template():
    template = get_template("web_app")
    assert template is not None
    assert template.template_type == "web_app"


def test_get_template_returns_none_for_unknown():
    template = get_template("unknown")
    assert template is None


def test_list_templates_returns_all():
    templates = list_templates()
    assert "web_app" in templates
    assert "api_service" in templates
    assert len(templates) >= 5


def test_all_template_phases_have_tasks():
    for template in TEMPLATES.values():
        for phase in template.phases:
            assert len(phase.tasks) > 0, f"{template.template_type}/{phase.name} has no tasks"


def test_all_template_tasks_have_ids():
    for template in TEMPLATES.values():
        for phase in template.phases:
            for task in phase.tasks:
                assert task.id, f"Task in {template.template_type} missing id"
                assert task.name, f"Task {task.id} in {template.template_type} missing name"