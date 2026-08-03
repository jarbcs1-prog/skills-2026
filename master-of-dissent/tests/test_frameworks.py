"""Tests for master-of-dissent frameworks."""
from scripts.frameworks import FRAMEWORKS


def test_framework_count():
    assert len(FRAMEWORKS) >= 5


def test_reductio_ad_absurdum_exists():
    assert "reductio_ad_absurdum" in FRAMEWORKS


def test_steel_manning_exists():
    assert "steel_manning" in FRAMEWORKS


def test_analogy_exists():
    assert "analogy" in FRAMEWORKS


def test_reframing_exists():
    assert "reframing" in FRAMEWORKS


def test_counter_example_exists():
    assert "counter_example" in FRAMEWORKS


def test_all_frameworks_have_templates():
    for name, fw in FRAMEWORKS.items():
        assert "template" in fw, f"Framework {name} missing template"


def test_all_frameworks_have_description():
    for name, fw in FRAMEWORKS.items():
        assert "description" in fw, f"Framework {name} missing description"


def test_reductio_template_contains_placeholder():
    fw = FRAMEWORKS["reductio_ad_absurdum"]
    assert "{premise}" in fw["template"] or "premise" in fw["template"].lower()


def test_steel_man_template_contains_placeholder():
    fw = FRAMEWORKS["steel_manning"]
    assert "{strong_form}" in fw["template"] or "strong_form" in fw["template"].lower()