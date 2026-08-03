"""Automated trust auditor for trust-psychology skill."""
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class TrustSignal:
    category: str
    name: str
    location: str
    effectiveness: float = 0.0
    verifiability: float = 0.0


@dataclass
class AuditResult:
    signals: List[TrustSignal] = field(default_factory=list)
    coverage: Dict[str, float] = field(default_factory=dict)
    effectiveness: float = 0.0
    gaps: List[str] = field(default_factory=list)
    killers: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    overall_score: float = 0.0


class TrustAuditor:
    SIGNAL_CATEGORIES = [
        "security_visual",
        "social_proof",
        "guarantees",
        "competence",
        "ai_transparency",
        "structural_assurance",
    ]

    RISK_TYPES = [
        "financial", "product", "service",
        "psychological", "privacy", "time",
    ]

    def __init__(self):
        self.signals_found: List[TrustSignal] = []

    def audit(self, page_content: str, context: str = "saas_signup") -> AuditResult:
        signals = self._extract_signals(page_content)
        coverage = self._assess_risk_coverage(signals, context)
        effectiveness = self._score_effectiveness(signals, context)
        gaps = self._identify_gaps(coverage, context)
        killers = self._detect_killers(page_content)
        recommendations = self._generate_recommendations(gaps, killers, context)
        score = self._calculate_score(effectiveness, coverage)

        return AuditResult(
            signals=signals,
            coverage=coverage,
            effectiveness=effectiveness,
            gaps=gaps,
            killers=killers,
            recommendations=recommendations,
            overall_score=score,
        )

    def _extract_signals(self, page_content: str) -> List[TrustSignal]:
        if not page_content.strip():
            return []
        signals = []
        for category in self.SIGNAL_CATEGORIES:
            signals.append(TrustSignal(
                category=category,
                name=f"{category}_signal",
                location="detected",
                effectiveness=0.5,
                verifiability=0.5,
            ))
        return signals

    def _assess_risk_coverage(self, signals: List[TrustSignal], context: str) -> Dict[str, float]:
        if not signals:
            return {}
        coverage = {}
        for risk in self.RISK_TYPES:
            coverage[risk] = 0.5
        return coverage

    def _score_effectiveness(self, signals: List[TrustSignal], context: str) -> float:
        if not signals:
            return 0.0
        return sum(s.effectiveness for s in signals) / len(signals)

    def _identify_gaps(self, coverage: Dict[str, float], context: str) -> List[str]:
        gaps = []
        for risk, score in coverage.items():
            if score < 0.7:
                gaps.append(f"Low coverage for {risk} risk (score: {score:.2f})")
        return gaps

    def _detect_killers(self, page_content: str) -> List[str]:
        killers = []
        if "no refund" in page_content.lower():
            killers.append("No refund policy mentioned")
        return killers

    def _generate_recommendations(self, gaps: List[str], killers: List[str], context: str) -> List[str]:
        recs = []
        for gap in gaps:
            recs.append(f"Address gap: {gap}")
        for killer in killers:
            recs.append(f"Remove trust killer: {killer}")
        return recs

    def _calculate_score(self, effectiveness: float, coverage: Dict[str, float]) -> float:
        if not self.signals_found and not coverage:
            return 0.0
        avg_coverage = sum(coverage.values()) / len(coverage) if coverage else 0.0
        return round((effectiveness + avg_coverage) / 2, 2)