"""Rhyme analysis for rap-writer skill."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class RhymePair:
    line_a: int
    line_b: int
    rhyme_type: str  # perfect, slant, assonance, consonance
    words: tuple[str, str]


@dataclass
class RhymeAnalysis:
    end_rhymes: list[RhymePair]
    internal_rhymes: list[RhymePair]
    rhyme_scheme: str
    multisyllabic: list[str]
    density: float


def _last_word(line: str) -> str:
    """Extract the last word from a line."""
    word = line.strip().split()[-1] if line.strip() else ""
    return word.lower().strip(".,;:!?\"'()[]{}")


def _phonetic_end(word: str) -> str:
    """Get the phonetic ending of a word (simplified)."""
    word = word.lower()
    # Simple heuristic: last 2-3 characters
    if len(word) >= 3:
        return word[-3:]
    if len(word) >= 2:
        return word[-2:]
    return word


def _is_perfect_rhyme(w1: str, w2: str) -> bool:
    """Check if two words have a perfect rhyme."""
    if not w1 or not w2:
        return False
    end1 = _phonetic_end(w1)
    end2 = _phonetic_end(w2)
    return end1 == end2 and w1 != w2


def _is_slant_rhyme(w1: str, w2: str) -> bool:
    """Check if two words have a slant rhyme (similar but not perfect)."""
    if not w1 or not w2:
        return False
    end1 = _phonetic_end(w1)
    end2 = _phonetic_end(w2)
    if len(end1) < 2 or len(end2) < 2:
        return False
    # Share at least the last 2 characters
    return end1[-2:] == end2[-2:] and w1 != w2


def find_end_rhymes(lines: list[str]) -> list[RhymePair]:
    """Find end rhymes between consecutive lines."""
    rhymes = []
    for i in range(len(lines) - 1):
        w1 = _last_word(lines[i])
        w2 = _last_word(lines[i + 1])
        if _is_perfect_rhyme(w1, w2):
            rhymes.append(RhymePair(i, i + 1, "perfect", (w1, w2)))
        elif _is_slant_rhyme(w1, w2):
            rhymes.append(RhymePair(i, i + 1, "slant", (w1, w2)))
    return rhymes


def find_internal_rhymes(lines: list[str]) -> list[RhymePair]:
    """Find internal rhymes within lines."""
    rhymes = []
    for i, line in enumerate(lines):
        words = line.lower().split()
        for j in range(len(words)):
            for k in range(j + 1, len(words)):
                w1 = words[j].strip(".,;:!?\"'()[]{}")
                w2 = words[k].strip(".,;:!?\"'()[]{}")
                if _is_perfect_rhyme(w1, w2):
                    rhymes.append(RhymePair(i, i, "perfect", (w1, w2)))
    return rhymes


def detect_scheme(lines: list[str]) -> str:
    """Detect rhyme scheme (AABB, ABAB, etc.)."""
    if len(lines) < 2:
        return "none"
    end_words = [_last_word(l) for l in lines]
    scheme = []
    seen = {}
    for i, w in enumerate(end_words):
        if w in seen:
            scheme.append(seen[w])
        else:
            label = chr(ord("A") + len(seen))
            seen[w] = label
            scheme.append(label)
    return "".join(scheme)


def find_multisyllabic(lines: list[str]) -> list[str]:
    """Find multisyllabic words in the lyrics."""
    multis = []
    for line in lines:
        for word in line.split():
            w = word.lower().strip(".,;:!?\"'()[]{}")
            if count_syllables_simple(w) >= 3:
                multis.append(w)
    return multis


def count_syllables_simple(word: str) -> int:
    """Simple syllable count."""
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    prev_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    return max(1, count)


def calculate_density(lines: list[str]) -> float:
    """Calculate rhyme density (rhymes per line)."""
    if not lines:
        return 0.0
    end_rhymes = find_end_rhymes(lines)
    return len(end_rhymes) / len(lines)


def analyze(lyrics: str) -> RhymeAnalysis:
    """Analyze rhyme patterns in lyrics."""
    lines = [l.strip() for l in lyrics.split("\n") if l.strip()]
    return RhymeAnalysis(
        end_rhymes=find_end_rhymes(lines),
        internal_rhymes=find_internal_rhymes(lines),
        rhyme_scheme=detect_scheme(lines),
        multisyllabic=find_multisyllabic(lines),
        density=calculate_density(lines),
    )
