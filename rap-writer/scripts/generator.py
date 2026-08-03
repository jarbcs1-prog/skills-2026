"""Lyric generation for rap-writer skill."""
from __future__ import annotations

import random
from dataclasses import dataclass

from scripts.styles import StyleProfile, STYLE_PROFILES
from scripts.rhythm import analyze as analyze_rhythm, LineRhythm
from scripts.rhyme import analyze as analyze_rhyme, RhymeAnalysis


@dataclass
class AdaptationConstraints:
    target_word_count: int
    preserve_rhyme: bool = True
    preserve_rhythm: bool = True
    style: str = "boom-bap"


@dataclass
class AdaptedLyrics:
    original: str
    adapted: str
    theme: str
    style: str
    word_count_match: bool
    rhyme_score: float
    rhythm_score: float


@dataclass
class GeneratedLyrics:
    lyrics: str
    style: str
    structure: list[str]
    theme: str


# Simple word banks for constrained generation
THEME_WORDS: dict[str, list[str]] = {
    "climate change": ["earth", "warming", "future", "green", "carbon", "ocean", "rising", "nature"],
    "startup life": [" hustle", " grind", " venture", " code", " launch", " pivot", " scale", " seed"],
    "daily struggles": ["morning", "grind", "survive", "struggle", "pay", "rent", "work", "sleep"],
    "technology": ["digital", "network", "data", "signal", "code", "machine", "cloud", "byte"],
    "social commentary": ["system", "power", "voice", "fight", "justice", "truth", "rights", "stand"],
}


def adapt(original: str, theme: str, constraints: AdaptationConstraints) -> AdaptedLyrics:
    """Adapt original lyrics to a new theme while preserving structure."""
    orig_analysis = analyze_rhythm(original)
    orig_rhyme = analyze_rhyme(original)

    style = STYLE_PROFILES.get(constraints.style, STYLE_PROFILES["boom-bap"])

    # Generate adapted lyrics
    adapted_lines = _generate_adapted_lines(original, theme, style, constraints)
    adapted = "\n".join(adapted_lines)

    # Score the adaptation
    adapted_analysis = analyze_rhythm(adapted)
    adapted_rhyme = analyze_rhyme(adapted)

    word_count_match = abs(len(adapted.split()) - len(original.split())) <= 2
    rhyme_score = _score_rhyme_preservation(orig_rhyme, adapted_rhyme)
    rhythm_score = _score_rhythm_match(orig_analysis, adapted_analysis)

    return AdaptedLyrics(
        original=original,
        adapted=adapted,
        theme=theme,
        style=constraints.style,
        word_count_match=word_count_match,
        rhyme_score=rhyme_score,
        rhythm_score=rhythm_score,
    )


def generate(theme: str, structure: list[str], style: str = "boom-bap") -> GeneratedLyrics:
    """Generate original lyrics from scratch."""
    style_profile = STYLE_PROFILES.get(style, STYLE_PROFILES["boom-bap"])
    theme_words = THEME_WORDS.get(theme, ["life", "love", "dream", "night", "city", "streets"])

    lines = []
    for section in structure:
        lines.append(f"[{section.upper()}]")
        for _ in range(4):
            line = _compose_line(theme_words, style_profile)
            lines.append(line)

    return GeneratedLyrics(
        lyrics="\n".join(lines),
        style=style,
        structure=structure,
        theme=theme,
    )


def _generate_adapted_lines(original: str, theme: str, style: StyleProfile, constraints: AdaptationConstraints) -> list[str]:
    """Generate adapted lines preserving structure."""
    orig_lines = [l.strip() for l in original.split("\n") if l.strip()]
    theme_words = THEME_WORDS.get(theme, ["life", "change", "world", "time", "moment"])

    adapted = []
    for orig_line in orig_lines:
        orig_word_count = len(orig_line.split())
        new_words = []
        for _ in range(orig_word_count):
            new_words.append(random.choice(theme_words))
        adapted.append(" ".join(new_words))

    return adapted if adapted else orig_lines


def _compose_line(theme_words: list[str], style: StyleProfile) -> str:
    """Compose a single line matching the style."""
    word_count = random.randint(4, 12)
    words = [random.choice(theme_words) for _ in range(word_count)]
    return " ".join(words)


def _score_rhyme_preservation(orig: RhymeAnalysis, adapted: RhymeAnalysis) -> float:
    """Score how well rhyme scheme is preserved."""
    if not orig.end_rhymes and not adapted.end_rhymes:
        return 1.0
    if not orig.end_rhymes:
        return 0.5
    orig_scheme = orig.rhyme_scheme
    adapted_scheme = adapted.rhyme_scheme
    if orig_scheme == adapted_scheme:
        return 1.0
    # Partial match
    matches = sum(1 for a, b in zip(orig_scheme, adapted_scheme) if a == b)
    return matches / max(len(orig_scheme), len(adapted_scheme))


def _score_rhythm_match(orig: RhythmAnalysis, adapted: RhythmAnalysis) -> float:
    """Score how well rhythm is preserved."""
    if not orig.lines or not adapted.lines:
        return 0.5
    orig_avg = sum(l.syllable_count for l in orig.lines) / len(orig.lines)
    adapted_avg = sum(l.syllable_count for l in adapted.lines) / len(adapted.lines)
    if orig_avg == 0:
        return 0.5
    similarity = 1.0 - abs(orig_avg - adapted_avg) / max(orig_avg, adapted_avg)
    return max(0.0, similarity)
