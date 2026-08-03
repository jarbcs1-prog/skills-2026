"""Style profiles for human-writer-simulator skill."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StyleProfile:
    name: str
    formality: float
    vocabulary_level: float
    sentence_complexity: float
    hedging: float
    personal_voice: float
    imperfections: list[str]
    forbidden: list[str]


STYLE_PROFILES: dict[str, StyleProfile] = {
    "conversational": StyleProfile(
        name="conversational",
        formality=0.2,
        vocabulary_level=0.4,
        sentence_complexity=0.3,
        hedging=0.5,
        personal_voice=0.9,
        imperfections=["colloquialisms", "sentence_fragments", "self_correction"],
        forbidden=["academic_transitions", "passive_voice"],
    ),
    "technical": StyleProfile(
        name="technical",
        formality=0.7,
        vocabulary_level=0.8,
        sentence_complexity=0.6,
        hedging=0.3,
        personal_voice=0.2,
        imperfections=["occasional_fragment", "inline_code_refs"],
        forbidden=["flowery_metaphors", "excessive_adjectives"],
    ),
    "executive": StyleProfile(
        name="executive",
        formality=0.8,
        vocabulary_level=0.7,
        sentence_complexity=0.5,
        hedging=0.2,
        personal_voice=0.4,
        imperfections=["direct_assertions", "strategic_pauses"],
        forbidden=["hedging", "rambling"],
    ),
    "creative": StyleProfile(
        name="creative",
        formality=0.4,
        vocabulary_level=0.8,
        sentence_complexity=0.7,
        hedging=0.4,
        personal_voice=0.8,
        imperfections=["metaphors", "rhythm_variation", "intentional_fragments"],
        forbidden=["bullet_points", "numbered_lists"],
    ),
    "academic": StyleProfile(
        name="academic",
        formality=0.9,
        vocabulary_level=0.9,
        sentence_complexity=0.8,
        hedging=0.4,
        personal_voice=0.1,
        imperfections=["citations", "qualified_statements"],
        forbidden=["colloquialisms", "contractions"],
    ),
}


def get_style(name: str) -> StyleProfile | None:
    """Retrieve a style profile by name."""
    return STYLE_PROFILES.get(name)


def list_styles() -> list[str]:
    """List all available style profiles."""
    return list(STYLE_PROFILES.keys())
