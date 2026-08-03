"""Tests for rap-writer style profiles."""
import pytest
from scripts.styles import STYLE_PROFILES, get_style, list_styles, StyleProfile


class TestStyleProfiles:
    def test_all_profiles_are_style_profile_instances(self):
        for name, profile in STYLE_PROFILES.items():
            assert isinstance(profile, StyleProfile)
            assert profile.name == name

    def test_profile_has_required_fields(self):
        profile = STYLE_PROFILES["boom-bap"]
        assert profile.bpm_range is not None
        assert isinstance(profile.bpm_range, tuple)
        assert len(profile.bpm_range) == 2
        assert profile.time_signature == "4/4"
        assert isinstance(profile.rhyme_density, float)
        assert isinstance(profile.multisyllabic_freq, float)
        assert isinstance(profile.internal_rhyme_freq, float)
        assert isinstance(profile.flow_patterns, list)
        assert isinstance(profile.typical_structure, list)

    def test_bpm_range_valid(self):
        for name, profile in STYLE_PROFILES.items():
            assert profile.bpm_range[0] < profile.bpm_range[1], f"{name} has invalid bpm_range"

    def test_rhyme_density_in_range(self):
        for name, profile in STYLE_PROFILES.items():
            assert 0.0 <= profile.rhyme_density <= 1.0, f"{name} rhyme_density out of range"

    def test_multisyllabic_freq_in_range(self):
        for name, profile in STYLE_PROFILES.items():
            assert 0.0 <= profile.multisyllabic_freq <= 1.0, f"{name} multisyllabic_freq out of range"

    def test_internal_rhyme_freq_in_range(self):
        for name, profile in STYLE_PROFILES.items():
            assert 0.0 <= profile.internal_rhyme_freq <= 1.0, f"{name} internal_rhyme_freq out of range"

    def test_all_profiles_have_flow_patterns(self):
        for name, profile in STYLE_PROFILES.items():
            assert len(profile.flow_patterns) > 0, f"{name} has no flow patterns"

    def test_all_profiles_have_structure(self):
        for name, profile in STYLE_PROFILES.items():
            assert len(profile.typical_structure) > 0, f"{name} has no structure"


class TestGetStyle:
    def test_get_existing_style(self):
        profile = get_style("boom-bap")
        assert profile is not None
        assert profile.name == "boom-bap"

    def test_get_nonexistent_style(self):
        assert get_style("nonexistent") is None

    def test_get_trap_style(self):
        profile = get_style("trap")
        assert profile is not None
        assert profile.bpm_range == (130, 160)


class TestListStyles:
    def test_list_returns_all_styles(self):
        styles = list_styles()
        assert len(styles) == len(STYLE_PROFILES)

    def test_list_contains_known_styles(self):
        styles = list_styles()
        assert "boom-bap" in styles
        assert "trap" in styles
        assert "conscious" in styles
        assert "drill" in styles
        assert "lo-fi" in styles

    def test_list_returns_copy(self):
        styles1 = list_styles()
        styles2 = list_styles()
        assert styles1 == styles2
