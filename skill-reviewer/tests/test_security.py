"""Tests for the skill-reviewer secret scanning."""

from scripts.skill_reviewer import security_scan


def test_detects_aws_key(tmp_path):
    skill = tmp_path / "leaky"
    skill.mkdir()
    (skill / "config.py").write_text(
        'aws_access_key_id = "AKIAIOSFODNN7EXAMPLE"\n',
        encoding="utf-8",
    )
    result = security_scan(skill)
    assert len(result["vulnerabilities"]) >= 1
    hit = next(v for v in result["vulnerabilities"] if v["pattern"] == "aws_access_key")
    assert hit["file"] == "config.py"
    assert hit["line"] == 1


def test_detects_private_key(tmp_path):
    skill = tmp_path / "keys"
    skill.mkdir()
    (skill / "id_rsa").write_text(
        "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA\n-----END RSA PRIVATE KEY-----\n",
        encoding="utf-8",
    )
    result = security_scan(skill)
    patterns = {v["pattern"] for v in result["vulnerabilities"]}
    assert "private_key" in patterns


def test_clean_skill_has_no_vulnerabilities(tmp_path):
    skill = tmp_path / "clean"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "# Clean\n\nNothing secret here.\n",
        encoding="utf-8",
    )
    assert security_scan(skill)["vulnerabilities"] == []


def test_detects_openai_style_key(tmp_path):
    skill = tmp_path / "tokens"
    skill.mkdir()
    (skill / ".env").write_text("OPENAI_API_KEY=sk-1234567890abcdefghijklmnop\n", encoding="utf-8")
    result = security_scan(skill)
    assert any(v["pattern"] == "openai_key" for v in result["vulnerabilities"])


def test_skips_binary_and_ignored_dirs(tmp_path):
    skill = tmp_path / "mixed"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# Mixed\n", encoding="utf-8")
    ignored = skill / ".git" / "config"
    ignored.parent.mkdir(parents=True)
    ignored.write_text("token = \"AAAAAAAAAAAAAAAAAAAAAAA\"\n", encoding="utf-8")
    result = security_scan(skill)
    assert result["vulnerabilities"] == []
