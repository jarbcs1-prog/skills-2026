"""Tests for trust-psychology auditor."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.auditor import TrustAuditor, AuditResult


def test_auditor_initializes():
    auditor = TrustAuditor()
    assert auditor.SIGNAL_CATEGORIES
    assert auditor.RISK_TYPES


def test_audit_returns_result():
    auditor = TrustAuditor()
    result = auditor.audit("<html>Test page</html>", "saas_signup")
    assert isinstance(result, AuditResult)
    assert len(result.signals) > 0
    assert result.overall_score >= 0.0


def test_audit_coverage():
    auditor = TrustAuditor()
    result = auditor.audit("<html>Test</html>", "ecommerce_checkout")
    assert result.coverage
    assert len(result.coverage) > 0


def test_audit_detects_killers():
    auditor = TrustAuditor()
    result = auditor.audit("<html>no refund policy</html>", "saas_signup")
    assert len(result.killers) > 0


def test_audit_recommendations():
    auditor = TrustAuditor()
    result = auditor.audit("<html>no refund policy</html>", "saas_signup")
    assert len(result.recommendations) > 0


def test_audit_empty_content():
    auditor = TrustAuditor()
    result = auditor.audit("", "saas_signup")
    assert result.overall_score == 0.0


def test_audit_signal_categories():
    auditor = TrustAuditor()
    result = auditor.audit("<html>Test</html>", "saas_signup")
    categories = {s.category for s in result.signals}
    assert "security_visual" in categories
    assert "social_proof" in categories