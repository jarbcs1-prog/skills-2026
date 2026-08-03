"""Tests for chinese-translator scripts."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run_cli(*args, cwd=None):
    result = subprocess.run(
        [sys.executable, "-m", "scripts.cli", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(cwd or ROOT),
    )
    return result


def test_domain_detection():
    from scripts.domains import detect_domain, DOMAIN_KEYWORDS

    assert detect_domain("合同要求赔偿损失") == "legal"
    assert detect_domain("服务器部署缓存接口") == "technical"
    assert detect_domain("患者诊断治疗方案") == "medical"
    assert detect_domain("营收增长市场投资") == "business"
    assert detect_domain("描写意象诗句情感") == "literary"
    assert detect_domain("品牌推广转化率用户") == "marketing"
    assert detect_domain("random unrelated text xyz") == "general"


def test_glossary():
    from scripts.glossary import Glossary

    g = Glossary()
    g.add("合同", "contract", "legal")
    g.add("赔偿", "damages", "legal")
    assert g.get("合同")["translation"] == "contract"
    # check violations
    text = "合同要求赔偿"  # both terms present, but no translations
    violations = g.check(text)
    assert len(violations) == 2
    # with translation present
    text2 = "合同 contract 要求 赔偿 damages"
    violations2 = g.check(text2)
    assert len(violations2) == 0


def test_translation_memory():
    from scripts.translation_memory import TranslationMemory

    tm = TranslationMemory()
    tm.add("你好", "Hello", "general")
    assert tm.lookup("你好")["translation"] == "Hello"
    assert tm.lookup("不存在") is None
    assert tm.hit_rate(["你好", "世界"]) == 0.5
    hits = tm.find_repeats("你好世界")
    assert any(h["source"] == "你好" for h in hits)


def test_quality_scores():
    from scripts.quality import compute_quality_scores, overall

    source = "合同要求赔偿损失"
    translation = "contract requires damages loss"
    scores = compute_quality_scores(source, translation)
    assert 0 <= scores["fluency"] <= 1
    assert 0 <= scores["adequacy"] <= 1
    assert scores["terminology_consistency"] == 1.0  # no glossary
    assert 0 <= overall(scores) <= 1


def test_translator_pipeline():
    from scripts.translator import ChineseTranslator, create_domain_glossary
    from scripts.glossary import Glossary

    # TM hit
    from scripts.translation_memory import TranslationMemory
    tm = TranslationMemory()
    tm.add("你好", "Hello", "general")
    translator = ChineseTranslator(tm=tm)
    result = translator.translate("你好", domain="auto")
    assert result["tm_hit"] is True
    assert result["translation"] == "Hello"

    # glossary substitution
    gl = create_domain_glossary("legal")
    translator2 = ChineseTranslator(glossary=gl)
    result2 = translator2.translate("合同要求赔偿", domain="legal")
    assert "[contract]" in result2["translation"]
    assert "[damages]" in result2["translation"]
    assert result2["tm_hit"] is False
    assert "quality_scores" in result2


def test_cli_translate():
    res = run_cli("translate", "合同要求赔偿")
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["source"] == "合同要求赔偿"
    assert "translation" in data
    assert data["domain"] in {"legal", "auto"}


def test_cli_translate_with_glossary(tmp_path):
    # create a glossary
    gl_file = tmp_path / "gl.json"
    res = run_cli("glossary", "create", "--domain", "legal", "--output", str(gl_file))
    assert res.returncode == 0

    # translate using it
    res2 = run_cli("translate", "合同要求赔偿", "--glossary", str(gl_file))
    assert res2.returncode == 0
    data = json.loads(res2.stdout)
    assert "[contract]" in data["translation"]


def test_cli_batch(tmp_path):
    # create input files
    in_dir = tmp_path / "in"
    in_dir.mkdir()
    (in_dir / "a.txt").write_text("合同\n条款", encoding="utf-8")
    (in_dir / "b.md").write_text("# 标题\n内容", encoding="utf-8")
    out_dir = tmp_path / "out"

    res = run_cli("batch", "--input", str(in_dir), "--output", str(out_dir))
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["processed"] == 2

    # check output exists
    assert (out_dir / "a.txt").exists()
    assert (out_dir / "b.md").exists()


def test_cli_validate():
    res = run_cli("validate", "--input", str(ROOT / "SKILL.md"), "--threshold", "0.1")
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert "quality_scores" in data
    assert "passed" in data


def test_cli_glossary_create(tmp_path):
    out = tmp_path / "legal_gl.json"
    res = run_cli("glossary", "create", "--domain", "legal", "--output", str(out))
    assert res.returncode == 0
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "合同" in data
    assert len(data) >= 6


def test_cli_glossary_check(tmp_path):
    gl = tmp_path / "gl.json"
    run_cli("glossary", "create", "--domain", "legal", "--output", str(gl))
    # check with translation present -> 0 violations
    res = run_cli("glossary", "check", "--text", "合同 contract 赔偿 damages", "--glossary", str(gl))
    assert res.returncode == 0
    data = json.loads(res.stdout)
    assert data["count"] == 0

    # check without translation -> violations
    res2 = run_cli("glossary", "check", "--text", "合同 要求 赔偿", "--glossary", str(gl))
    data2 = json.loads(res2.stdout)
    assert data2["count"] >= 2


def test_cli_tm_add(tmp_path):
    tm_file = tmp_path / "tm.json"
    res = run_cli("tm", "add", "--tm", str(tm_file), "--source", "测试", "--translation", "Test", "--domain", "general")
    assert res.returncode == 0
    res2 = run_cli("tm", "lookup", "--tm", str(tm_file), "--text", "测试")
    assert res2.returncode == 0
    data = json.loads(res2.stdout)
    assert data["translation"] == "Test"


def test_cli_no_command():
    res = run_cli()
    assert res.returncode == 2


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))