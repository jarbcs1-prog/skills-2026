"""Safety filters for master-of-dissent skill."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FilteredResponse:
    allowed: bool
    reason: str = ""
    safe_alternative: str = ""


class DissentSafety:
    BLOCKED_TARGETS: list[str] = [
        "personal_appearance",
        "protected_characteristics",
        "mental_health",
        "family_personal_life",
        "trauma",
        "insecurities",
    ]

    ALLOWED_TARGETS: list[str] = [
        "ideas_arguments",
        "code_quality",
        "technical_decisions",
        "process_methodology",
        "tool_choices",
        "boasting_claims",
        "logical_inconsistencies",
    ]

    def filter(self, response: str, target: str) -> FilteredResponse:
        if target in self.BLOCKED_TARGETS:
            return FilteredResponse(
                allowed=False,
                reason=f"Target '{target}' is protected",
                safe_alternative=self._generate_safe_redirect(target),
            )
        return FilteredResponse(allowed=True)

    def _generate_safe_redirect(self, target: str) -> str:
        redirects = {
            "personal_appearance": "Focus on the argument, not the person",
            "protected_characteristics": "Address the idea, not the identity",
            "mental_health": "Redirect to the technical substance",
            "family_personal_life": "Keep the discussion professional",
            "trauma": "Acknowledge with care, then refocus",
            "insecurities": "Build up rather than tear down",
        }
        return redirects.get(target, "Refocus on the topic at hand")

    def is_allowed_target(self, target: str) -> bool:
        return target in self.ALLOWED_TARGETS
