from __future__ import annotations

from scripts.rules import PERFORMANCE_RULES, rules_for_language, scan_source

CONCAT_SNIPPET = '''def render():
    out = ""
    for i in range(3):
        out = out += "x"
    return out
'''

N_PLUS_ONE_SNIPPET = '''for user in users:
    rows = db.query("SELECT * FROM orders WHERE user_id=%s", user.id)
'''


def test_rules_for_language_python() -> None:
    rules = rules_for_language("python")
    ids = [rule["id"] for rule in rules]
    assert rules
    assert "py-string-concat-loop" in ids


def test_rules_total_count() -> None:
    total = sum(len(rules) for rules in PERFORMANCE_RULES.values())
    assert total >= 15
    assert all(language in PERFORMANCE_RULES for language in ("python", "database", "javascript", "rust", "go"))


def test_scan_detects_string_concat() -> None:
    findings = scan_source(CONCAT_SNIPPET, "python")
    concat = [finding for finding in findings if finding["rule_id"] == "py-string-concat-loop"]
    assert len(concat) == 1
    assert concat[0]["line"] == 4
    assert concat[0]["severity"] == "HIGH"
    assert concat[0]["message"]


def test_scan_detects_n_plus_one() -> None:
    findings = scan_source(N_PLUS_ONE_SNIPPET, "database")
    n_plus_one = [finding for finding in findings if finding["rule_id"] == "db-n-plus-one"]
    assert len(n_plus_one) == 1
    assert n_plus_one[0]["line"] == 1
    assert n_plus_one[0]["severity"] == "CRITICAL"


def test_select_star_fires() -> None:
    findings = scan_source("SELECT * FROM users", "database")
    assert any(finding["rule_id"] == "db-select-star" for finding in findings)


def test_scan_unknown_language_empty() -> None:
    assert scan_source("for x in y: pass", "cobol") == []
