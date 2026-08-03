"""Trust signal component library for trust-psychology skill."""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TrustSignalProps:
    type: str
    variant: str = "badge"
    priority: str = "essential"
    context: str = "header"


@dataclass
class SecurityBadge:
    badge: str = "ssl"
    size: str = "md"

    BADGES = {
        "ssl": {"icon": "🔒", "label": "SSL Secured", "verification": "https://..."},
        "payment": {"icon": "💳", "label": "Secure Payment", "verification": "https://..."},
        "privacy": {"icon": "🛡️", "label": "Privacy Protected", "verification": "https://..."},
    }

    def render(self) -> str:
        info = self.BADGES.get(self.badge, self.BADGES["ssl"])
        return f"{info['icon']} {info['label']} ({info['verification']})"


@dataclass
class SocialProof:
    variant: str = "testimonials"
    count: int = 3

    def render(self) -> str:
        return f"Social proof ({self.variant}): {self.count} items"


@dataclass
class Guarantee:
    type: str = "money-back"
    duration: str = "30-day"

    GUARANTEES = {
        "money-back": {"label": "Money-Back Guarantee", "period": "30-day"},
        "free_trial": {"label": "Free Trial", "period": "14-day"},
        "no_credit_card": {"label": "No Credit Card Required", "period": "N/A"},
        "cancellation": {"label": "Cancel Anytime", "period": "N/A"},
    }

    def render(self) -> str:
        info = self.GUARANTEES.get(self.type, self.GUARANTEES["money-back"])
        return f"{info['label']} ({info['period']})"


TRUST_COMPONENTS = {
    "security_badge": SecurityBadge,
    "social_proof": SocialProof,
    "guarantee": Guarantee,
}


def get_component(name: str) -> Optional[type]:
    return TRUST_COMPONENTS.get(name)


def list_components() -> List[str]:
    return list(TRUST_COMPONENTS.keys())