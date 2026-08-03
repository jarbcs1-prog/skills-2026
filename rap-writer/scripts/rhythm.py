"""Rhythm analysis for rap-writer skill."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class LineRhythm:
    syllable_count: int
    stress_pattern: str
    meter: str
    pause_count: int


@dataclass
class RhythmAnalysis:
    lines: list[LineRhythm]
    overall_meter: str
    tempo_hint: str


SIMPLE_VOWELS = re.compile(r'[aeiouyAEIOUY]+')


def count_syllables(word: str) -> int:
    """Count syllables in a word using vowel group heuristic."""
    word = word.lower().strip(".,;:!?\"'()[]{}")
    if not word:
        return 0
    vowels = SIMPLE_VOWELS.findall(word)
    count = len(vowels)
    # Adjust for common patterns
    if word.endswith("e") and count > 1:
        count -= 1
    if word.endswith("le") and len(word) > 2 and word[-3] not in "aeiouy":
        count += 1
    return max(1, count)


def analyze_line(line: str) -> LineRhythm:
    """Analyze rhythm of a single lyric line."""
    words = line.split()
    syllable_counts = [count_syllables(w) for w in words]
    total_syllables = sum(syllable_counts)

    # Simple stress pattern: capitalize every other syllable
    stress = ""
    for i, syl in enumerate(syllable_counts):
        for j in range(syl):
            stress += "S" if (i + j) % 2 == 0 else "W"

    # Classify meter
    if total_syllables <= 4:
        meter = "short"
    elif total_syllables <= 8:
        meter = "medium"
    else:
        meter = "long"

    # Count pauses (commas, periods, dashes)
    pause_count = line.count(",") + line.count(".") + line.count("—") + line.count(";")

    return LineRhythm(
        syllable_count=total_syllables,
        stress_pattern=stress,
        meter=meter,
        pause_count=pause_count,
    )


def detect_meter(lines: list[str]) -> str:
    """Detect overall meter from a list of lines."""
    if not lines:
        return "unknown"
    meters = [analyze_line(l).meter for l in lines]
    # Return most common meter
    from collections import Counter
    return Counter(meters).most_common(1)[0][0]


def estimate_tempo(lines: list[str]) -> str:
    """Estimate tempo hint from line lengths and pause patterns."""
    if not lines:
        return "moderate"
    avg_syllables = sum(analyze_line(l).syllable_count for l in lines) / len(lines)
    avg_pauses = sum(analyze_line(l).pause_count for l in lines) / len(lines)

    if avg_syllables > 12 and avg_pauses < 1:
        return "fast"
    if avg_syllables < 6 and avg_pauses > 2:
        return "slow"
    return "moderate"


def analyze(lyrics: str) -> RhythmAnalysis:
    """Analyze rhythm of full lyrics."""
    lines = [l.strip() for l in lyrics.split("\n") if l.strip()]
    line_analyses = [analyze_line(l) for l in lines]
    return RhythmAnalysis(
        lines=line_analyses,
        overall_meter=detect_meter(lines),
        tempo_hint=estimate_tempo(lines),
    )
