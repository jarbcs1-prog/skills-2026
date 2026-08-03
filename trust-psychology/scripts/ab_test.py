"""A/B testing framework for trust-psychology skill."""
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ExperimentConfig:
    name: str
    control_variant: str
    treatment_variant: str
    metric: str
    sample_size: int = 1000
    confidence_level: float = 0.95
    minimum_effect_size: float = 0.1


@dataclass
class ExperimentResult:
    experiment_name: str
    control_conversion: float
    treatment_conversion: float
    lift: float
    p_value: float
    statistically_significant: bool
    confidence_interval: tuple
    effect_size: float
    segment_analysis: Dict[str, float] = field(default_factory=dict)


class TrustABTest:
    def __init__(self):
        self.experiments: List[ExperimentConfig] = []

    def create_experiment(self, config: ExperimentConfig) -> ExperimentConfig:
        self.experiments.append(config)
        return config

    def analyze(self, config: ExperimentConfig,
                control_rate: float,
                treatment_rate: float) -> ExperimentResult:
        lift = (treatment_rate - control_rate) / control_rate if control_rate > 0 else 0.0
        p_value = self._calculate_p_value(control_rate, treatment_rate, config.sample_size)
        significant = p_value < (1 - config.confidence_level)
        ci = self._confidence_interval(control_rate, treatment_rate, config.sample_size, config.confidence_level)
        effect_size = self._cohens_d(control_rate, treatment_rate)

        return ExperimentResult(
            experiment_name=config.name,
            control_conversion=control_rate,
            treatment_conversion=treatment_rate,
            lift=lift,
            p_value=p_value,
            statistically_significant=significant,
            confidence_interval=ci,
            effect_size=effect_size,
        )

    def _calculate_p_value(self, control: float, treatment: float, n: int) -> float:
        import math
        if n <= 0:
            return 1.0
        se = math.sqrt(control * (1 - control) / n + treatment * (1 - treatment) / n)
        if se == 0:
            return 1.0
        z = (treatment - control) / se
        return max(0.0, min(1.0, 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))))

    def _confidence_interval(self, control: float, treatment: float,
                              n: int, confidence: float) -> tuple:
        import math
        z_critical = 1.96 if confidence == 0.95 else 2.576
        se = math.sqrt(control * (1 - control) / n + treatment * (1 - treatment) / n)
        diff = treatment - control
        return (diff - z_critical * se, diff + z_critical * se)

    def _cohens_d(self, control: float, treatment: float) -> float:
        pooled_std = ((control * (1 - control) + treatment * (1 - treatment)) / 2) ** 0.5
        if pooled_std == 0:
            return 0.0
        return (treatment - control) / pooled_std