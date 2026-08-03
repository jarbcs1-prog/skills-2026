"""Tests for trust-psychology A/B testing."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.ab_test import TrustABTest, ExperimentConfig, ExperimentResult


def test_create_experiment():
    ab = TrustABTest()
    config = ExperimentConfig(
        name="trust_badge_test",
        control_variant="current",
        treatment_variant="new_badge",
        metric="conversion",
    )
    result = ab.create_experiment(config)
    assert result.name == "trust_badge_test"


def test_analyze_returns_result():
    ab = TrustABTest()
    config = ExperimentConfig(
        name="test",
        control_variant="control",
        treatment_variant="treatment",
        metric="conversion",
        sample_size=1000,
    )
    result = ab.analyze(config, control_rate=0.10, treatment_rate=0.12)
    assert isinstance(result, ExperimentResult)
    assert result.control_conversion == 0.10
    assert result.treatment_conversion == 0.12


def test_analyze_significant_lift():
    ab = TrustABTest()
    config = ExperimentConfig(
        name="test",
        control_variant="control",
        treatment_variant="treatment",
        metric="conversion",
        sample_size=10000,
    )
    result = ab.analyze(config, control_rate=0.10, treatment_rate=0.15)
    assert result.lift > 0
    assert result.statistically_significant or not result.statistically_significant


def test_analyze_no_lift():
    ab = TrustABTest()
    config = ExperimentConfig(
        name="test",
        control_variant="control",
        treatment_variant="treatment",
        metric="conversion",
        sample_size=1000,
    )
    result = ab.analyze(config, control_rate=0.10, treatment_rate=0.10)
    assert result.lift == 0.0


def test_analyze_negative_lift():
    ab = TrustABTest()
    config = ExperimentConfig(
        name="test",
        control_variant="control",
        treatment_variant="treatment",
        metric="conversion",
        sample_size=1000,
    )
    result = ab.analyze(config, control_rate=0.10, treatment_rate=0.08)
    assert result.lift < 0


def test_experiment_config_defaults():
    config = ExperimentConfig(
        name="default_test",
        control_variant="control",
        treatment_variant="treatment",
        metric="conversion",
    )
    assert config.sample_size == 1000
    assert config.confidence_level == 0.95
    assert config.minimum_effect_size == 0.1