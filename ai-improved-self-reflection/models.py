"""
AI Self-Reflection Engine v2

Core data models.

The system separates:

Experience Memory:
    What happened during a task.

Reflection Candidates:
    Generalized lessons extracted from experiences.

Capability Memory:
    Validated improvements that influence future behavior.

Validation:
    Evidence that a capability actually improved outcomes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


SCHEMA_VERSION = 2


class FrictionType(str, Enum):
    """
    Categories from the reflection framework.
    """

    STRUCTURAL = "structural"
    EPISTEMIC = "epistemic"
    INTERACTION = "interaction"
    STRATEGY = "strategy"
    UNKNOWN = "unknown"


class PromotionLevel(str, Enum):
    """
    Capability maturity levels.

    Observation:
        Single event.

    Candidate:
        Repeated pattern requiring validation.

    Local:
        Useful within a domain/context.

    Global:
        General capability update.
    """

    OBSERVATION = "observation"
    CANDIDATE = "candidate"
    LOCAL = "local"
    GLOBAL = "global"


class ObservationStatus(str, Enum):
    """
    Lifecycle state for unseen observations.
    """

    MONITORING = "monitoring"
    CONVERTED = "converted"
    DISCARDED = "discarded"


@dataclass
class CommunicationAudit:
    """
    Captures interaction friction signals.

    These measure communication mismatch rather than task correctness.
    """

    audience_assumptions: List[str] = field(default_factory=list)

    hidden_criteria: List[str] = field(default_factory=list)

    corrections: int = 0

    clarifications: int = 0

    re_prompts: int = 0

    def communication_score(self) -> float:
        """
        Returns a quality score between 0 and 1.

        Higher is better.

        Corrections have the largest penalty because they indicate
        stronger mismatch between output and user intent.
        """

        penalty = (
            self.corrections * 0.10
            + self.clarifications * 0.05
            + self.re_prompts * 0.03
        )

        return max(
            0.0,
            min(
                1.0,
                1.0 - penalty,
            ),
        )


@dataclass
class ReflectionEvent:
    """
    Experience Memory.

    Represents what happened before interpretation.
    """

    task: str

    category: str

    friction: str

    friction_type: FrictionType

    observation: str

    root_cause: str

    lesson: str

    scope: str

    confidence: float

    evidence_count: int

    action: str

    communication: CommunicationAudit = field(
        default_factory=CommunicationAudit
    )

    created: str = field(
        default_factory=lambda:
            datetime.now().isoformat()
    )

    schema_version: int = SCHEMA_VERSION


@dataclass
class ReflectionCandidate:
    """
    Generalization layer.

    A possible reusable principle extracted from
    multiple experiences.
    """

    lesson: str

    scope: str

    source_events: int

    confidence: float

    transferability: float

    validation_required: bool = True

    status: ObservationStatus = (
        ObservationStatus.MONITORING
    )

    created: str = field(
        default_factory=lambda:
            datetime.now().isoformat()
    )

    schema_version: int = SCHEMA_VERSION


@dataclass
class Capability:
    """
    Capability Memory.

    Only validated improvements become capabilities.
    """

    name: str

    principle: str

    scope: List[str]

    evidence_count: int

    confidence: float

    validation_score: float

    promotion_level: PromotionLevel

    active: bool = True

    last_validated: Optional[str] = None

    created: str = field(
        default_factory=lambda:
            datetime.now().isoformat()
    )

    schema_version: int = SCHEMA_VERSION


@dataclass
class ValidationRecord:
    """
    Evidence that a capability improved outcomes.
    """

    capability_name: str

    task: str

    outcome: str

    improvement_observed: bool

    confidence_delta: float

    created: str = field(
        default_factory=lambda:
            datetime.now().isoformat()
    )

    schema_version: int = SCHEMA_VERSION


@dataclass
class UnseenObservation:
    """
    Temporary holding area.

    Represents the "unseen layer":

    Interesting signals that may become useful,
    but are not yet ready for behavior change.
    """

    observation: str

    possible_category: str

    status: ObservationStatus = (
        ObservationStatus.MONITORING
    )

    evidence_count: int = 1

    created: str = field(
        default_factory=lambda:
            datetime.now().isoformat()
    )

    schema_version: int = SCHEMA_VERSION
