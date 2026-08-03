"""Style profiles for rap-writer skill."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StyleProfile:
    name: str
    bpm_range: tuple[int, int]
    time_signature: str
    rhyme_density: float
    multisyllabic_freq: float
    internal_rhyme_freq: float
    vocabulary_level: str
    flow_patterns: list[str]
    typical_structure: list[str]


STYLE_PROFILES: dict[str, StyleProfile] = {
    "boom-bap": StyleProfile(
        name="boom-bap",
        bpm_range=(85, 95),
        time_signature="4/4",
        rhyme_density=0.7,
        multisyllabic_freq=0.6,
        internal_rhyme_freq=0.4,
        vocabulary_level="street_poetic",
        flow_patterns=["straight", "syncopated"],
        typical_structure=["verse", "chorus", "verse", "chorus", "bridge", "chorus"],
    ),
    "trap": StyleProfile(
        name="trap",
        bpm_range=(130, 160),
        time_signature="4/4",
        rhyme_density=0.5,
        multisyllabic_freq=0.3,
        internal_rhyme_freq=0.2,
        vocabulary_level="street_modern",
        flow_patterns=["triplet", "double_time", "straight"],
        typical_structure=["verse", "chorus", "verse", "chorus", "verse", "chorus"],
    ),
    "conscious": StyleProfile(
        name="conscious",
        bpm_range=(80, 95),
        time_signature="4/4",
        rhyme_density=0.8,
        multisyllabic_freq=0.7,
        internal_rhyme_freq=0.5,
        vocabulary_level="literary_philosophical",
        flow_patterns=["straight", "syncopated", "rubato"],
        typical_structure=["verse", "verse", "chorus", "verse", "chorus", "outro"],
    ),
    "drill": StyleProfile(
        name="drill",
        bpm_range=(140, 170),
        time_signature="4/4",
        rhyme_density=0.4,
        multisyllabic_freq=0.2,
        internal_rhyme_freq=0.1,
        vocabulary_level="street_ominous",
        flow_patterns=["straight", "slow_drawl"],
        typical_structure=["verse", "chorus", "verse", "chorus", "verse"],
    ),
    "lo-fi": StyleProfile(
        name="lo-fi",
        bpm_range=(60, 80),
        time_signature="4/4",
        rhyme_density=0.6,
        multisyllabic_freq=0.5,
        internal_rhyme_freq=0.3,
        vocabulary_level="casual_contemplative",
        flow_patterns=["rubato", "syncopated", "straight"],
        typical_structure=["verse", "verse", "chorus", "bridge", "chorus"],
    ),
}


def get_style(name: str) -> StyleProfile | None:
    """Retrieve a style profile by name."""
    return STYLE_PROFILES.get(name)


def list_styles() -> list[str]:
    """List all available style profiles."""
    return list(STYLE_PROFILES.keys())
