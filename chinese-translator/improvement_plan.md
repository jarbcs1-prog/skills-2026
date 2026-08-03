# Improvement Plan: chinese-translator

## Current State Assessment

**Tier:** 🔴 Critically Thin (Needs Complete Rewrite)
**Lines:** 13 | **Version:** 1.0 (implied)

### Strengths
- Clear role definition (translator, editor, spell checker)
- Handles Simplified Chinese, Mandarin, Cantonese
- Specifies output constraints (no explanations unless requested)
- Single-word translation with examples

### Gaps Identified
1. **No workflow or process** - Just role description
2. **No quality validation** - No way to verify translation accuracy
3. **No domain specialization** - General only (legal, technical, literary, business)
4. **No terminology management** - No glossary, consistency checking
5. **No batch processing** - Single item only
6. **No integration points** - Standalone only
7. **No examples or test cases**
8. **No handling of ambiguity** - Multiple valid translations
9. **No cultural adaptation** - Localization vs translation
10. **No tooling** - No CLI, no API, no quality gates

---

## Improvement Roadmap

### Phase 1: Core Workflow (Week 1)
- [ ] Define translation workflow: Analyze → Translate → Review → Validate
- [ ] Add domain detection (auto or manual): legal, technical, medical, business, literary, marketing
- [ ] Implement terminology glossary with consistency checking
- [ ] Add translation memory for repeated phrases

### Phase 2: Quality Assurance (Week 2)
- [ ] Add back-translation validation (translate back, compare semantics)
- [ ] Implement quality metrics: fluency, adequacy, terminology consistency
- [ ] Add ambiguity detection and resolution options
- [ ] Create translation review checklist

### Phase 3: Tooling & Automation (Week 3)
- [ ] Build CLI with commands: translate, batch, validate, glossary
- [ ] Add file format support: .txt, .md, .docx, .xlsx, .srt, .po
- [ ] Implement batch processing with progress tracking
- [ ] Add API wrapper for programmatic use

### Phase 4: Advanced Features (Week 4)
- [ ] Add localization support (currency, dates, units, cultural references)
- [ ] Implement style guide enforcement (formal/informal, brand voice)
- [ ] Add machine translation post-editing (MTPE) workflow
- [ ] Create translation project management (multiple files, glossaries, reviewers)

---

## Specific Technical Tasks

### Translation Workflow
```python
# translator.py
class ChineseTranslator:
    def translate(self, text: str, domain: Domain = AUTO, 
                  style: Style = NEUTRAL, glossary: Glossary = None) -> TranslationResult:
        # 1. Analyze: detect domain, extract terms, identify ambiguities
        # 2. Translate: apply domain rules, glossary, style guide
        # 3. Review: back-translate, check consistency, flag issues
        # 4. Validate: quality scores, human review flags
        return TranslationResult(
            translation=...,
            quality_scores=...,
            flags=...,
            glossary_updates=...
        )
```

### Domain Definitions
```python
# domains.py
DOMAINS = {
    "legal": {
        "terminology_source": "blacks_law_dictionary",
        "style": "formal_precise",
        "validation": "legal_review_required"
    },
    "technical": {
        "terminology_source": "microsoft_terminology",
        "style": "concise_precise",
        "validation": "technical_accuracy_check"
    },
    "medical": {
        "terminology_source": "icd10_snomed",
        "style": "clinical_precise",
        "validation": "medical_review_required"
    },
    "business": {
        "terminology_source": "business_chinese_corpus",
        "style": "professional_natural",
        "validation": "business_sense_check"
    },
    "literary": {
        "terminology_source": "literary_corpus",
        "style": "expressive_nuanced",
        "validation": "literary_quality_assessment"
    },
    "marketing": {
        "terminology_source": "brand_guidelines",
        "style": "persuasive_cultural",
        "validation": "cultural_appropriateness"
    }
}
```

### CLI Commands
```bash
# chinese-translator translate "text" --domain technical --style formal
# chinese-translator batch input.md --output output.md --glossary glossary.json
# chinese-translator validate translation.txt --back-translate --threshold 0.85
# chinese-translator glossary create --domain legal --output legal_glossary.json
# chinese-translator glossary check translation.txt --glossary legal_glossary.json
```

### Quality Metrics
```python
# quality.py
def compute_quality_scores(source: str, translation: str, back_translation: str) -> QualityScores:
    return QualityScores(
        fluency=fluency_score(translation),           # Language model perplexity
        adequacy=semantic_similarity(source, back_translation),  # Embedding similarity
        terminology_consistency=glossary_adherence(translation, glossary),
        style_conformance=style_classifier(translation, target_style),
        cultural_appropriateness=cultural_check(translation, target_locale)
    )
```

---

## Acceptance Criteria
- [ ] CLI handles all 6 file formats with batch processing
- [ ] Domain detection accuracy >90% on test corpus
- [ ] Quality scores correlate with human evaluation >0.8
- [ ] Glossary consistency checking catches >95% of term violations
- [ ] Back-translation validation threshold configurable
- [ ] Translation memory reduces repeat work >50%
- [ ] MTPE workflow reduces post-edit time >30%

---

## Dependencies
- `code-quality` for CLI code quality
- `verification-before-completion` for quality claims
- `doc-reader` for document format support
- `xlsx` for spreadsheet translation

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Domain detection errors | High | Medium | Manual override, confidence scoring |
| Cultural inappropriateness | Medium | High | Native reviewer flag, cultural check |
| Terminology inconsistency | High | Medium | Glossary enforcement, automated check |
| File format corruption | Low | High | Format-preserving translation, validation |

---

## Success Metrics
- Translation quality (BLEU/comet): >0.85 vs human reference
- Terminology consistency: 100% glossary adherence
- Batch processing speed: >1000 words/minute
- User satisfaction: >4.5/5
- Domain coverage: 6 domains with validated glossaries