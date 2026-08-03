"""Tests for conversation templates."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.templates import (
    FEEDBACK_TEMPLATE, TERMINATION_TEMPLATE, CONFLICT_TEMPLATE, NEGOTIATION_TEMPLATE
)


def test_feedback_template_has_all_fields():
    assert FEEDBACK_TEMPLATE.name
    assert FEEDBACK_TEMPLATE.type == "feedback"
    assert FEEDBACK_TEMPLATE.framework
    assert len(FEEDBACK_TEMPLATE.preparation) > 0
    assert len(FEEDBACK_TEMPLATE.flow) > 0
    assert len(FEEDBACK_TEMPLATE.common_reactions) > 0
    assert len(FEEDBACK_TEMPLATE.follow_up) > 0


def test_termination_template_has_all_fields():
    assert TERMINATION_TEMPLATE.name
    assert TERMINATION_TEMPLATE.type == "termination"
    assert TERMINATION_TEMPLATE.framework


def test_conflict_template_has_all_fields():
    assert CONFLICT_TEMPLATE.name
    assert CONFLICT_TEMPLATE.type == "conflict"
    assert CONFLICT_TEMPLATE.framework


def test_negotiation_template_has_all_fields():
    assert NEGOTIATION_TEMPLATE.name
    assert NEGOTIATION_TEMPLATE.type == "negotiation"
    assert NEGOTIATION_TEMPLATE.framework


def test_all_templates_have_framework():
    for template in [FEEDBACK_TEMPLATE, TERMINATION_TEMPLATE,
                     CONFLICT_TEMPLATE, NEGOTIATION_TEMPLATE]:
        assert template.framework, f"{template.type} missing framework"


def test_all_templates_have_preparation_steps():
    for template in [FEEDBACK_TEMPLATE, TERMINATION_TEMPLATE,
                     CONFLICT_TEMPLATE, NEGOTIATION_TEMPLATE]:
        assert len(template.preparation) > 0, f"{template.type} missing preparation"


def test_all_templates_have_flow_steps():
    for template in [FEEDBACK_TEMPLATE, TERMINATION_TEMPLATE,
                     CONFLICT_TEMPLATE, NEGOTIATION_TEMPLATE]:
        assert len(template.flow) > 0, f"{template.type} missing flow"


def test_all_templates_have_follow_up():
    for template in [FEEDBACK_TEMPLATE, TERMINATION_TEMPLATE,
                     CONFLICT_TEMPLATE, NEGOTIATION_TEMPLATE]:
        assert len(template.follow_up) > 0, f"{template.type} missing follow_up"