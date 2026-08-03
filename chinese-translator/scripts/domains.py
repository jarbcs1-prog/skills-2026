"""Domain definitions and detection for Chinese translation."""

from __future__ import annotations

DOMAINS = {
    "legal": {
        "terminology_source": "blacks_law_dictionary",
        "style": "formal_precise",
        "validation": "legal_review_required",
    },
    "technical": {
        "terminology_source": "microsoft_terminology",
        "style": "concise_precise",
        "validation": "technical_accuracy_check",
    },
    "medical": {
        "terminology_source": "icd10_snomed",
        "style": "clinical_precise",
        "validation": "medical_review_required",
    },
    "business": {
        "terminology_source": "business_chinese_corpus",
        "style": "professional_natural",
        "validation": "business_sense_check",
    },
    "literary": {
        "terminology_source": "literary_corpus",
        "style": "expressive_nuanced",
        "validation": "literary_quality_assessment",
    },
    "marketing": {
        "terminology_source": "brand_guidelines",
        "style": "persuasive_cultural",
        "validation": "cultural_appropriateness",
    },
}

DOMAIN_ORDER = ("legal", "technical", "medical", "business", "literary", "marketing")

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "legal": [
        "合同",
        "法律",
        "赔偿",
        "条款",
        "甲方",
        "乙方",
        "责任",
        "协议",
        "agreement",
        "liability",
        "contract",
        "clause",
        "damages",
        "indemnify",
    ],
    "technical": [
        "接口",
        "服务器",
        "部署",
        "缓存",
        "数据库",
        "框架",
        "api",
        "cloud",
        "deployment",
        "endpoint",
        "latency",
        "service",
        "compute",
        "database",
    ],
    "medical": [
        "患者",
        "诊断",
        "剂量",
        "治疗",
        "症状",
        "处方",
        "patient",
        "diagnosis",
        "dosage",
        "treatment",
        "symptom",
        "prescription",
        "clinical",
    ],
    "business": [
        "营收",
        "市场",
        "投资",
        "利润",
        "股东",
        "增长",
        "revenue",
        "market",
        "investment",
        "margin",
        "stakeholder",
        "growth",
        "quarterly",
        "earnings",
    ],
    "literary": [
        "描写",
        "意象",
        "比喻",
        "叙事",
        "情感",
        "诗句",
        "imagery",
        "metaphor",
        "narrative",
        "prose",
        "verse",
        "theme",
        "lyrical",
    ],
    "marketing": [
        "品牌",
        "用户",
        "推广",
        "营销",
        "转化率",
        "定位",
        "brand",
        "campaign",
        "audience",
        "conversion",
        "positioning",
        "promotion",
        "awareness",
    ],
}


def detect_domain(text: str) -> str:
    """Return the best-matching domain for ``text`` or ``general`` when no match."""
    lower = text.lower()
    best_domain = "general"
    best_hits = 0
    for domain in DOMAIN_ORDER:
        hits = sum(1 for kw in DOMAIN_KEYWORDS[domain] if kw.lower() in lower)
        if hits > best_hits:
            best_hits = hits
            best_domain = domain
    return best_domain


def domain_style(domain: str) -> str:
    """Return the recommended style string for a domain (falls back to neutral)."""
    entry = DOMAINS.get(domain)
    return entry["style"] if entry else "neutral"
