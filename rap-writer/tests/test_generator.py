"""Tests for rap-writer lyric generator."""
import pytest
from scripts.generator import (
    AdaptationConstraints,
    AdaptedLyrics,
    GeneratedLyrics,
    adapt,
    generate,
    THEME_WORDS,
)


class TestAdapt:
    def test_adapt_returns_adapted_lyrics(self):
        original = "Hello world this is a test"
        result = adapt(original, "technology", AdaptationConstraints(target_word_count=10))
        assert isinstance(result, AdaptedLyrics)
        assert result.original == original
        assert result.theme == "technology"
        assert result.style == "boom-bap"

    def test_adapt_preserves_word_count_approximately(self):
        original = "Hello world this is a test line"
        result = adapt(original, "technology", AdaptationConstraints(target_word_count=20))
        # Word count should be close (within 2 as per constraints)
        assert abs(len(result.adapted.split()) - len(original.split())) <= 2

    def test_adapt_with_custom_style(self):
        original = "Hello world this is a test"
        result = adapt(original, "climate change", AdaptationConstraints(target_word_count=10, style="trap"))
        assert result.style == "trap"

    def test_adapt_with_custom_theme(self):
        original = "Hello world this is a test"
        result = adapt(original, "startup life", AdaptationConstraints(target_word_count=10))
        assert result.theme == "startup life"

    def test_adapt_scores_present(self):
        original = "Hello world this is a test line with more words"
        result = adapt(original, "technology", AdaptationConstraints(target_word_count=15))
        assert isinstance(result.rhyme_score, float)
        assert isinstance(result.rhythm_score, float)
        assert 0.0 <= result.rhyme_score <= 1.0
        assert 0.0 <= result.rhythm_score <= 1.0

    def test_adapt_preserves_rhyme_default(self):
        original = "The cat sat on the mat"
        result = adapt(original, "daily struggles", AdaptationConstraints(target_word_count=10, preserve_rhyme=True))
        assert result.adapted is not None


class TestGenerate:
    def test_generate_returns_generated_lyrics(self):
        result = generate("technology", ["verse", "chorus"])
        assert isinstance(result, GeneratedLyrics)
        assert result.theme == "technology"
        assert result.style == "boom-bap"
        assert result.structure == ["verse", "chorus"]

    def test_generate_has_lyrics_content(self):
        result = generate("technology", ["verse", "chorus"])
        assert len(result.lyrics) > 0
        assert "[VERSE]" in result.lyrics
        assert "[CHORUS]" in result.lyrics

    def test_generate_with_custom_style(self):
        result = generate("startup life", ["verse", "chorus"], style="trap")
        assert result.style == "trap"

    def test_generate_multiple_sections(self):
        result = generate("daily struggles", ["verse", "chorus", "verse", "outro"])
        assert "[VERSE]" in result.lyrics
        assert "[CHORUS]" in result.lyrics
        assert "[OUTRO]" in result.lyrics

    def test_generate_uses_default_theme_words_for_unknown_theme(self):
        result = generate("unknown theme", ["verse"])
        assert result.lyrics is not None
        assert len(result.lyrics) > 0

    def test_generate_structure_preserved(self):
        structure = ["verse", "chorus", "bridge", "chorus"]
        result = generate("climate change", structure)
        assert result.structure == structure


class TestThemeWords:
    def test_known_themes_exist(self):
        assert "climate change" in THEME_WORDS
        assert "startup life" in THEME_WORDS
        assert "daily struggles" in THEME_WORDS
        assert "technology" in THEME_WORDS
        assert "social commentary" in THEME_WORDS

    def test_theme_words_are_non_empty(self):
        for theme, words in THEME_WORDS.items():
            assert len(words) > 0, f"Theme '{theme}' has no words"

    def test_theme_words_are_strings(self):
        for theme, words in THEME_WORDS.items():
            for word in words:
                assert isinstance(word, str), f"Theme '{theme}' has non-string word: {word}"
