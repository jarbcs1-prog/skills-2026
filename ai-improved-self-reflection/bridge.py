"""
AI Self-Reflection Engine v2

Bridge Orchestration Layer:

Connects qualitative capabilities memory with runtime
agent prompt assembly while enforcing strict token
context budgets.

This module bridges the gap between validated
capability memory and the agent's system prompt,
ensuring that only the most relevant, high-confidence
capabilities are injected into the runtime context.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List

from storage import (
    load_json,
)

import storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(
    "RuntimeReflectionBridge"
)


@dataclass
class TokenBudget:
    """
    Controls how many tokens the bridge
    may consume in the system prompt overlay.

    The bridge uses a simple character-based
    estimation: max_capability_tokens multiplied
    by avg_chars_per_token gives the maximum
    character budget for directive text.
    """

    max_capability_tokens: int = 500

    avg_chars_per_token: float = 4.0


class RuntimeReflectionBridge:
    """
    Bridge between capability memory and agent
    system prompt generation.

    Responsibilities:

    - Query capability memory for active entries
    - Filter by scope and promotion level
    - Rank by composite performance score
    - Generate a compact prompt overlay
    - Enforce token budget limits
    """

    def __init__(
        self,
        budget: TokenBudget = None,
    ):
        if budget is None:
            budget = TokenBudget()

        self.budget = budget

    def get_active_capabilities(
        self,
        current_scope: str,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves active capabilities filtered by
        scope and promotion criteria.

        A capability is included if:

        - It is marked active
        - Its scope list contains current_scope,
          contains 'general', or is empty
        - Its promotion_level is 'global' OR
          the scope matches

        Results are ranked by composite performance
        score: validation_score multiplied by confidence.
        """

        memory = load_json(
            storage.CAPABILITY_MEMORY,
            {},
        )

        capabilities = memory.get(
            "capabilities",
            [],
        )

        valid_caps: List[Dict[str, Any]] = []

        for cap in capabilities:
            if not cap.get("active", False):
                continue

            cap_scopes = [
                s.lower().strip()
                for s in cap.get("scope", [])
            ]

            is_global = (
                cap.get("promotion_level")
                == "global"
            )

            scope_match = (
                current_scope.lower().strip()
                in cap_scopes
                or "general" in cap_scopes
                or not cap_scopes
            )

            if is_global or scope_match:
                valid_caps.append(cap)

        valid_caps.sort(
            key=lambda x: (
                x.get("validation_score", 0.5)
                * x.get("confidence", 0.5)
            ),
            reverse=True,
        )

        logger.info(
            f"Found {len(valid_caps)} active "
            f"capabilities for scope '{current_scope}'"
        )

        return valid_caps

    def build_system_prompt_overlay(
        self,
        current_scope: str,
    ) -> str:
        """
        Formats active capabilities into a compact
        prompt injection block.

        Truncates directives when the token saturation
        threshold is reached, ensuring the overlay
        never exceeds the configured TokenBudget.
        """

        capabilities = self.get_active_capabilities(
            current_scope,
        )

        if not capabilities:
            logger.info(
                "No active capabilities found; "
                "returning empty overlay"
            )
            return ""

        header = (
            "\n### OPERATIONAL CONSTRAINTS "
            "(Self-Correction Directives)\n"
        )

        directives: List[str] = []

        current_chars = len(header)

        max_chars = int(
            self.budget.max_capability_tokens
            * self.budget.avg_chars_per_token
        )

        for cap in capabilities:
            directive = (
                f"- [{cap['name']}]: "
                f"{cap['principle']}"
            )

            if (
                current_chars
                + len(directive)
                + 1
                > max_chars
            ):
                logger.info(
                    f"Token limit reached after "
                    f"{len(directives)} directives; "
                    f"truncating remaining "
                    f"{len(capabilities) - len(directives)} "
                    f"capabilities"
                )
                break

            directives.append(directive)

            current_chars += (
                len(directive) + 1
            )

        overlay = (
            header
            + "\n".join(directives)
            + "\n"
        )

        logger.info(
            f"Generated prompt overlay: "
            f"{len(directives)} directives, "
            f"~{current_chars} chars"
        )

        return overlay


if __name__ == "__main__":
    bridge = RuntimeReflectionBridge()

    overlay = bridge.build_system_prompt_overlay(
        "general"
    )

    print(
        "\n--- Generated Prompt Overlay ---"
    )

    if overlay:
        print(overlay)
    else:
        print("[No active capabilities found]")
