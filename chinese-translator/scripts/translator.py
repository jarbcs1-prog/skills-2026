"""Translation pipeline: analyze → translate → review → validate."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from scripts.domains import detect_domain
from scripts.glossary import Glossary
from scripts.translation_memory import TranslationMemory
from scripts.quality import compute_quality_scores, overall


class ChineseTranslator:
    """Deterministic Chinese→English translation pipeline with glossary/TM support."""

    def __init__(
        self,
        glossary: Optional[Glossary] = None,
        tm: Optional[TranslationMemory] = None,
    ) -> None:
        self.glossary = glossary
        self.tm = tm

    def analyze(self, text: str) -> dict:
        """Analyze source text for domain, terminology, ambiguities, cultural items."""
        domain = detect_domain(text)
        flags = []
        # ambiguity: term in multiple glossary domains
        if self.glossary:
            for term in self.glossary.terms:
                if term in text:
                    term_domains = set()
                    for k, v in self.glossary.terms.items():
                        if k == term:
                            term_domains.add(v.get("domain", "general"))
                    if len(term_domains) > 1:
                        flags.append({"type": "ambiguity", "message": f"Term '{term}' has multiple domain translations"})
        # cultural items: currency / dates
        if re.search(r"[¥$€£]\s?\d", text) or re.search(r"\b\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}\b", text):
            flags.append({"type": "cultural", "message": "Localization may be required for currency or dates"})
        return {
            "domain": domain,
            "sentence_count": len([s for s in re.split(r"[.!?。！？]+", text) if s.strip()]),
            "terms_found": [t for t in (self.glossary.terms if self.glossary else {}) if t in text],
            "flags": flags,
        }

    def _apply_glossary(self, text: str) -> str:
        if not self.glossary:
            return text
        result = text
        # sort terms by length desc to avoid partial replacements
        for term in sorted(self.glossary.terms.keys(), key=len, reverse=True):
            info = self.glossary.terms[term]
            result = result.replace(term, f"[{info['translation']}]")
        return result

    def translate(
        self,
        text: str,
        domain: str = "auto",
        style: str = "neutral",
        glossary: Optional[Glossary] = None,
        tm: Optional[TranslationMemory] = None,
    ) -> dict:
        """Full pipeline: TM lookup → glossary substitution → quality scores."""
        glossary = glossary or self.glossary
        tm = tm or self.tm

        # TM exact match
        tm_hit = False
        tm_entry = None
        if tm:
            lookup_domain = None if domain == "auto" else domain
            hit = tm.lookup(text, lookup_domain)
            if hit:
                tm_hit = True
                tm_entry = hit
                return {
                    "source": text,
                    "translation": hit["translation"],
                    "domain": hit.get("domain", domain),
                    "style": style,
                    "flags": [],
                    "quality_scores": {},
                    "glossary_updates": [],
                    "tm_hit": True,
                    "tm_entry": tm_entry,
                }

        # glossary substitution
        translation = self._apply_glossary(text)
        glossary_updates = []
        if glossary:
            for term in glossary.terms:
                if term in text:
                    glossary_updates.append(term)

        # flags
        flags = self.analyze(text).get("flags", [])

        # quality scores
        scores = compute_quality_scores(text, translation, None, glossary)

        return {
            "source": text,
            "translation": translation,
            "domain": domain if domain != "auto" else detect_domain(text),
            "style": style,
            "flags": flags,
            "quality_scores": scores,
            "glossary_updates": glossary_updates,
            "tm_hit": False,
        }

    def validate(self, text: str, translation: str, threshold: float = 0.5) -> dict:
        """Return quality scores and pass/fail against threshold."""
        scores = compute_quality_scores(text, translation, None, self.glossary)
        passed = scores.get("adequacy", 0) >= threshold and overall(scores) >= threshold
        return {
            "quality_scores": scores,
            "overall": overall(scores),
            "passed": passed,
            "threshold": threshold,
        }


def translate_file(
    input_path: str,
    output_path: str,
    translator: ChineseTranslator,
    domain: str = "auto",
    style: str = "neutral",
) -> dict:
    """Translate a text file, preserving format for .md/.txt/.srt/.po."""
    path = Path(input_path)
    ext = path.suffix.lower()
    text = path.read_text(encoding="utf-8")

    if ext == ".po":
        # simple msgid/msgstr parsing
        lines = text.splitlines()
        out_lines = []
        for line in lines:
            if line.startswith("msgid "):
                out_lines.append(line)
                continue
            if line.startswith("msgstr ") and line.strip() == 'msgstr ""':
                msgid = out_lines[-1][6:] if out_lines else ""
                if msgid:
                    res = translator.translate(msgid, domain, style)
                    out_lines.append(f'msgstr "{res["translation"]}"')
                else:
                    out_lines.append(line)
                continue
            out_lines.append(line)
        Path(output_path).write_text("\n".join(out_lines), encoding="utf-8")
    elif ext == ".srt":
        # preserve timestamps and indices, translate text blocks
        out_lines = []
        for line in text.splitlines():
            if re.match(r"^\d+$", line.strip()) or "-->" in line:
                out_lines.append(line)
            elif line.strip():
                res = translator.translate(line.strip(), domain, style)
                out_lines.append(res["translation"])
            else:
                out_lines.append(line)
        Path(output_path).write_text("\n".join(out_lines), encoding="utf-8")
    else:
        # plain text / markdown: translate each non-empty line
        out_lines = []
        for line in text.splitlines():
            if line.strip():
                res = translator.translate(line.strip(), domain, style)
                out_lines.append(res["translation"])
            else:
                out_lines.append(line)
        Path(output_path).write_text("\n".join(out_lines), encoding="utf-8")

    return {"processed": 1, "output": output_path}


# helper for CLI: create seeded glossary per domain
DOMAIN_GLOSSARIES = {
    "legal": {
        "合同": "contract",
        "赔偿": "damages",
        "条款": "clause",
        "甲方": "Party A",
        "乙方": "Party B",
        "责任": "liability",
        "协议": "agreement",
    },
    "technical": {
        "接口": "interface",
        "服务器": "server",
        "部署": "deployment",
        "缓存": "cache",
        "数据库": "database",
        "框架": "framework",
        "延迟": "latency",
    },
    "medical": {
        "患者": "patient",
        "诊断": "diagnosis",
        "剂量": "dosage",
        "治疗": "treatment",
        "症状": "symptom",
        "处方": "prescription",
    },
    "business": {
        "营收": "revenue",
        "市场": "market",
        "投资": "investment",
        "利润": "profit",
        "股东": "shareholder",
        "增长": "growth",
    },
    "literary": {
        "描写": "description",
        "意象": "imagery",
        "比喻": "metaphor",
        "叙事": "narrative",
        "情感": "emotion",
        "诗句": "verse",
    },
    "marketing": {
        "品牌": "brand",
        "用户": "user",
        "推广": "promotion",
        "营销": "marketing",
        "转化率": "conversion rate",
        "定位": "positioning",
    },
}


def create_domain_glossary(domain: str) -> Glossary:
    g = Glossary()
    terms = DOMAIN_GLOSSARIES.get(domain, {})
    for t, tr in terms.items():
        g.add(t, tr, domain)
    return g