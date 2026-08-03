from __future__ import annotations

from pathlib import Path

from scripts.rules_engine import (
    RULES,
    RULES_BY_ID,
    LANGUAGE_EXTENSIONS,
    infer_language,
    review_files,
    rules_for_category,
    rules_for_language,
    scan_file,
    scan_text,
    summarize,
    to_sarif,
)


def test_rule_count_and_coverage():
    assert len(RULES) >= 50
    categories = {r.category for r in RULES}
    assert {"security", "performance", "correctness", "maintainability", "testing"} <= categories
    severities = {r.severity for r in RULES}
    assert severities <= {"CRITICAL", "HIGH", "MEDIUM", "LOW"}


def test_unique_rule_ids():
    ids = [r.id for r in RULES]
    assert len(ids) == len(set(ids))
    assert set(RULES_BY_ID) == set(ids)


def test_rules_for_category():
    assert all(r.category == "security" for r in rules_for_category("security"))
    assert len(rules_for_category("security")) >= 10


def test_rules_for_language_filter():
    python_rules = rules_for_language("python")
    ids = {r.id for r in python_rules}
    assert "correctness-bare-except" in ids
    assert "security-xss-inner-html" not in ids


def test_language_extensions():
    assert LANGUAGE_EXTENSIONS[".py"] == "python"
    assert infer_language("api/users.py") == "python"
    assert infer_language("web/app.tsx") == "typescript"
    assert infer_language("lib/main.rs") == "rust"
    assert infer_language("README.md") == "unknown"


def test_scan_sql_injection():
    text = 'query = f"SELECT * FROM users WHERE id = {user_id}"'
    findings = scan_text(text, "python")
    assert any(f["rule_id"] == "security-sql-injection" for f in findings)
    assert all(f["line"] >= 1 for f in findings)


def test_scan_xss_inner_html():
    text = "element.innerHTML = userInput;"
    findings = scan_text(text, "javascript")
    assert any(f["rule_id"] == "security-xss-inner-html" for f in findings)


def test_scan_bare_except():
    text = "try:\n    risky()\nexcept:\n    pass"
    findings = scan_text(text, "python")
    assert any(f["rule_id"] == "correctness-bare-except" for f in findings)


def test_scan_hardcoded_secret():
    text = 'api_key = "sk-1234567890abcdefghij"'
    findings = scan_text(text, "python")
    assert any(f["rule_id"] == "security-hardcoded-secret" for f in findings)


def test_scan_clean_file_no_findings():
    text = "def add(a: int, b: int) -> int:\n    return a + b\n"
    findings = scan_text(text, "python")
    assert findings == []


def test_scan_file_missing_returns_empty(tmp_path: Path):
    assert scan_file(tmp_path / "nope.py") == []


def test_scan_file_reports_file_and_line(tmp_path: Path):
    bad = tmp_path / "bad.py"
    bad.write_text('x = "SELECT * FROM t WHERE id = " + uid\n', encoding="utf-8")
    findings = scan_file(bad)
    assert findings
    assert findings[0]["file"] == str(bad)
    assert findings[0]["language"] == "python"
    assert findings[0]["line"] == 1


def test_review_files_glob(tmp_path: Path):
    (tmp_path / "a.py").write_text('q = f"SELECT * FROM x"', encoding="utf-8")
    (tmp_path / "b.py").write_text("def ok(): pass\n", encoding="utf-8")
    result = review_files(["*.py"], cwd=tmp_path)
    assert result["files_scanned"] == [str(tmp_path / "a.py"), str(tmp_path / "b.py")]
    assert len(result["findings"]) >= 1


def test_review_files_deduplicates(tmp_path: Path):
    (tmp_path / "a.py").write_text('q = f"SELECT * FROM x"', encoding="utf-8")
    result = review_files(["a.py", "a.py"], cwd=tmp_path)
    assert len(result["files_scanned"]) == 1


def test_summary_score():
    findings = [{"severity": "CRITICAL"}, {"severity": "HIGH"}, {"severity": "MEDIUM"}, {"severity": "LOW"}]
    summary = summarize(findings)
    assert summary["total_findings"] == 4
    assert summary["score"] == 100 - 10 - 5 - 3 - 1
    assert summary["by_severity"] == {"CRITICAL": 1, "HIGH": 1, "MEDIUM": 1, "LOW": 1}
    assert summarize([{"severity": "CRITICAL"} for _ in range(20)])["score"] == 0


def test_to_sarif_structure():
    findings = [
        {
            "rule_id": "security-sql-injection",
            "rule_category": "security",
            "severity": "CRITICAL",
            "message": "bad",
            "fix": "fix it",
            "file": "x.py",
            "line": 3,
        }
    ]
    sarif = to_sarif(findings)
    assert sarif["version"] == "2.1.0"
    run = sarif["runs"][0]
    assert run["tool"]["driver"]["name"] == "code-reviewer"
    assert run["results"][0]["level"] == "error"
    assert run["results"][0]["locations"][0]["physicalLocation"]["region"]["startLine"] == 3
