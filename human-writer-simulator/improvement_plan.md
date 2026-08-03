# Improvement Plan: human-writer-simulator

## Current State Assessment

**Tier:** 🔴 Critically Thin (Needs Complete Rewrite)
**Lines:** 44 | **Version:** 1.0 (implied)

### Strengths
- Clear goal: eliminate AI-generated content features
- Specific rewrite workflow (5 steps)
- Output constraints (no explanations, direct output)
- Style guidelines (colloquial, imperfections, personal flair)

### Gaps Identified
1. **No detection capabilities** - Can't identify AI-written text
2. **No style profiles** - Single "human" style only
3. **No quality validation** - No way to measure human-likeness
4. **No domain adaptation** - Technical, creative, business, academic
5. **No batch processing** - Single paragraph only
6. **No tooling** - Manual rewrite only
7. **No integration** - Standalone skill
8. **No imperfection calibration** - "Minor imperfections" undefined
9. **No tone control** - Formal, casual, authoritative, friendly
10. **No examples** - No before/after comparisons

---

## Improvement Roadmap

### Phase 1: Detection & Analysis (Week 1)
- [ ] Build AI-text detector (perplexity, burstiness, stylometric features)
- [ ] Implement human-likeness scorer (multi-dimensional)
- [ ] Add style profiling (formal, casual, technical, narrative, persuasive)
- [ ] Create tone analyzer (authority, warmth, confidence, certainty)

### Phase 2: Rewrite Engine (Week 2)
- [ ] Build rewrite engine with configurable style profiles
- [ ] Add domain-specific adaptations (technical, marketing, academic, creative)
- [ ] Implement controlled imperfection injection (calibrated)
- [ ] Add tone preservation (don't change meaning, just style)

### Phase 3: Tooling & Automation (Week 3)
- [ ] Create CLI: detect, analyze, rewrite, batch
- [ ] Add file format support (txt, md, docx, html)
- [ ] Implement batch processing with progress
- [ ] Create API wrapper for programmatic use

### Phase 4: Quality & Integration (Week 4)
- [ ] Add human evaluation benchmark (blind test)
- [ ] Implement A/B testing for rewrite variants
- [ ] Add integration with `stop-slop` and `ghostwriter-pro-ai`
- [ ] Create style guide compliance checker

---

## Specific Technical Tasks

### AI Detection
```python
# detector.py
class AITextDetector:
    def __init__(self):
        self.features = [
            PerplexityFeature(),
            BurstinessFeature(), 
            RepetitionFeature(),
            TransitionFeature(),
            VocabularyDiversityFeature(),
            SentenceStructureFeature(),
            HedgingFeature(),
            StructureFeature()
        ]
    
    def analyze(self, text: str) -> DetectionResult:
        scores = {f.name: f.score(text) for f in self.features}
        ai_probability = self.classify(scores)
        return DetectionResult(
            ai_probability=ai_probability,
            feature_scores=scores,
            confidence=self.confidence(scores),
            indicators=self.get_indicators(scores)
        )
    
    def classify(self, scores: Dict[str, float]) -> float:
        # Weighted combination, calibrated on human/AI corpus
        weights = {
            "perplexity": 0.25,
            "burstiness": 0.20,
            "repetition": 0.15,
            "transitions": 0.10,
            "vocab_diversity": 0.10,
            "sentence_structure": 0.10,
            "hedging": 0.05,
            "structure": 0.05
        }
        return sum(scores[k] * w for k, w in weights.items())
```

### Human-Likeness Scorer
```python
# scorer.py
class HumanLikenessScorer:
    DIMENSIONS = {
        "naturalness": 0.25,      # Flows like human speech
        "personality": 0.20,      # Distinctive voice
        "imperfection": 0.15,     # Controlled flaws
        "coherence": 0.15,        # Logical but not rigid
        "emotional_range": 0.15,  # Appropriate affect
        "contextual_fit": 0.10    # Matches situation
    }
    
    def score(self, text: str, target_style: StyleProfile) -> HumanScore:
        # Multi-dimensional scoring with explanations
        pass
```

### Style Profiles
```python
# styles.py
STYLE_PROFILES = {
    "technical": StyleProfile(
        name="technical",
        formality=0.7,
        vocabulary_level=0.8,
        sentence_complexity=0.6,
        hedging=0.3,
        personal_voice=0.2,
        imperfections=["occasional_fragment", "inline_code_refs"],
        forbidden=["flowery_metaphors", "excessive_adjectives"]
    ),
    "conversational": StyleProfile(
        name="conversational",
        formality=0.2,
        vocabulary_level=0.4,
        sentence_complexity=0.3,
        hedging=0.5,
        personal_voice=0.9,
        imperfections=["colloquialisms", "sentence_fragments", "self_correction"],
        forbidden=["academic_transitions", "passive_voice"]
    ),
    "executive": StyleProfile(
        name="executive",
        formality=0.8,
        vocabulary_level=0.7,
        sentence_complexity=0.5,
        hedging=0.2,
        personal_voice=0.4,
        imperfections=["direct_assertions", "strategic_pauses"],
        forbidden=["hedging", "rambling"]
    ),
    "creative": StyleProfile(
        name="creative",
        formality=0.4,
        vocabulary_level=0.8,
        sentence_complexity=0.7,
        hedging=0.4,
        personal_voice=0.8,
        imperfections=["metaphors", "rhythm_variation", "intentional_fragments"],
        forbidden=["bullet_points", "numbered_lists"]
    )
}
```

### Rewrite Engine
```python
# rewriter.py
class HumanRewriter:
    def __init__(self, style: StyleProfile = None, 
                 imperfection_level: float = 0.3,
                 preserve_tone: bool = True):
        self.style = style or STYLE_PROFILES["conversational"]
        self.imperfection_level = imperfection_level
        self.preserve_tone = preserve_tone
    
    def rewrite(self, text: str, 
                domain: Domain = None,
                constraints: RewriteConstraints = None) -> RewriteResult:
        # 1. Analyze source (meaning, structure, key points)
        # 2. Plan rewrite (structure, voice, imperfections)
        # 3. Generate with style profile
        # 4. Inject calibrated imperfections
        # 5. Validate meaning preservation
        # 6. Score human-likeness
        pass
    
    def inject_imperfections(self, text: str) -> str:
        # Calibrated by imperfection_level (0-1)
        # Types: colloquialisms, fragments, self-corrections, 
        #        rhythm variation, personal asides
        pass
```

### CLI Design
```bash
# human-writer detect "text to analyze" --detailed
# human-writer analyze document.md --style-profile technical
# human-writer rewrite input.txt --style conversational --imperfections 0.4
# human-writer batch input_dir/ --output output_dir/ --style executive
# human-writer compare original.txt rewritten.txt --blind-test
# human-writer calibrate --samples human_samples/ ai_samples/
```

---

## Acceptance Criteria
- [ ] AI detection AUC >0.9 on benchmark corpus
- [ ] Human-likeness score correlates with human judges >0.8
- [ ] Rewrite preserves meaning >95% (semantic similarity)
- [ ] Style profile adherence >90% (automated check)
- [ ] Imperfection injection calibrated (blind test 50/50)
- [ ] Batch processes 1000 words/sec
- [ ] Domain adaptation for 5+ domains

---

## Dependencies
- `stop-slop` (complementary - removes AI patterns)
- `ghostwriter-pro-ai` (complementary - generates human-like)
- `code-quality` (CLI code)
- `verification-before-completion` (quality claims)
- `docs-write` (documentation)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Meaning drift | High | Critical | Semantic validation, back-translation check |
| Over-humanization | Medium | High | Constrained imperfection levels, tone preservation |
| Style inconsistency | Medium | Medium | Profile validation, coherence scoring |
| Detection evasion | Medium | Low | Multi-feature, regular recalibration |

---

## Success Metrics
- Blind test human/AI confusion: >40% misclassification
- Meaning preservation: >0.95 cosine similarity
- Style accuracy: >90% profile compliance
- User preference: >70% prefer rewritten version
- Processing speed: >500 words/second