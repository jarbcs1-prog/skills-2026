"""Tests for trust-psychology components."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.components import (
    SecurityBadge, SocialProof, Guarantee,
    get_component, list_components,
)


def test_security_badge_render():
    badge = SecurityBadge(badge="ssl", size="md")
    output = badge.render()
    assert "SSL Secured" in output


def test_security_badge_payment():
    badge = SecurityBadge(badge="payment")
    output = badge.render()
    assert "Secure Payment" in output


def test_social_proof_render():
    proof = SocialProof(variant="testimonials", count=5)
    output = proof.render()
    assert "Social proof" in output


def test_guarantee_money_back():
    guarantee = Guarantee(type="money-back", duration="30-day")
    output = guarantee.render()
    assert "Money-Back Guarantee" in output


def test_guarantee_free_trial():
    guarantee = Guarantee(type="free_trial")
    output = guarantee.render()
    assert "Free Trial" in output


def test_get_component():
    component = get_component("security_badge")
    assert component is SecurityBadge


def test_get_unknown_component():
    component = get_component("unknown")
    assert component is None


def test_list_components():
    components = list_components()
    assert "security_badge" in components
    assert "social_proof" in components
    assert "guarantee" in components