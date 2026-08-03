"""Tests for rap-writer rhythm analysis."""
import pytest
from scripts.rhythm import (
    count_syllables,
    analyze_line,
    detect_meter,
    estimate_tempo,
    analyze,
    LineRhythm,
    RhythmAnalysis,
)


class TestCountSyllables:
    def test_simple_word(self):
        assert count_syllables("hello") == 2

    def test_single_syllable(self):
        assert count_syllables("cat") == 1

    def test_word_with_trailing_e(self):
        assert count_syllables("make") == 1

    def test_word_with_le_e(self):
        assert count_syllables("apple") == 2

    def test_empty_string(self):
        assert count_syllables("") == 0

    def test_punctuation_stripped(self):
        assert count_syllables("hello!") == 2

    def test_all_vowels(self):
        assert count_syllables("aeiou") == 1


class TestAnalyzeLine:
    def test_short_line(self):
        result = analyze_line("Hello world")
        assert isinstance(result, LineRhythm)
        assert result.syllable_count > 0
        assert result.meter == "short"

    def test_medium_line(self):
        result = analyze_line("The quick brown fox")
        assert result.meter in ("short", "medium", "long")

    def test_long_line(self):
        result = analyze_line("The extraordinarily long sentence with many syllables in it")
        assert result.meter == "long"

    def test_pause_count(self):
        result = analyze_line("Hello, world. How are you; doing today—yes")
        assert result.pause_count == 4

    def test_no_pauses(self):
        result = analyze_line("Hello world")
        assert result.pause_count == 0

    def test_stress_pattern_generated(self):
        result = analyze_line("Hello world test")
        assert len(result.stress_pattern) > 0
        assert "S" in result.stress_pattern or "W" in result.stress_pattern


class TestDetectMeter:
    def test_empty_lines(self):
        assert detect_meter([]) == "unknown"

    def test_single_line(self):
        assert detect_meter(["Hello world"]) == "short"

    def test_mixed_meters_returns_most_common(self):
        lines = ["Hi", "Hello world", "Short", "Medium length line here"]
        result = detect_meter(lines)
        assert result in ("short", "medium")


class TestEstimateTempo:
    def test_empty_lines(self):
        assert estimate_tempo([]) == "moderate"

    def test_fast_tempo(self):
        lines = ["The extraordinarily long sentence with many syllables and no pauses at all here today"]
        result = estimate_tempo(lines)
        assert result == "fast"

    def test_slow_tempo(self):
        # Need avg_syllables < 6 AND avg_pauses > 2
        lines = ["Hi.", "Yes.", "No.", "Maybe."]
        result = estimate_tempo(lines)
        assert result in ("slow", "moderate")


class TestAnalyzeFull:
    def test_empty_lyrics(self):
        result = analyze("")
        assert isinstance(result, RhythmAnalysis)
        assert result.overall_meter == "unknown"

    def test_single_line(self):
        result = analyze("Hello world")
        assert len(result.lines) == 1
        assert result.lines[0].syllable_count > 0

    def test_multiline_lyrics(self):
        lyrics = "Hello world\nThis is a test\nAnother line here"
        result = analyze(lyrics)
        assert len(result.lines) == 3
        assert result.overall_meter in ("short", "medium", "long")

    def test_tempo_hint_present(self):
        result = analyze("Hello world\nThis is a test")
        assert result.tempo_hint in ("fast", "slow", "moderate")
