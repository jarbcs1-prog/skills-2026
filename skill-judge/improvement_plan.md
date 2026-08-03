# Improvement Plan: skill-judge

## Current State Assessment

**Tier:** 🟢 Production-Ready (Minor Polish)
**Lines:** 350 | **Version:** 1.0 (implied)

### Strengths
- 8-dimensional evaluation framework (120 points total)
- Knowledge Delta as core dimension (20 pts) - paradigm shifting
- Clear scoring rubrics with red/green flags for each dimension
- Three knowledge types classification (Expert/Activation/Redundant)
- Pattern recognition with 6 official patterns
- Mandatory reference loading for consistent evaluation
- Self-evaluation command
- Decision-prompt triggers for reference loading
- Quick reference checklist

### Gaps Identified
1. **Reference files missing** - 5 references referenced but not present
2. **No automated evaluator** - Manual only, no CLI/script
3. **No calibration benchmarks** - No standard skills for scoring calibration
4. **No historical tracking** - Can't track skill quality over time
5. **No integration with skill-creator** - Should be quality gate in creation loop
6. **No batch evaluation** - Single skill only
7. **No report templates** - Only Quick Reference mentioned
8. **No skill comparison** - Can't compare multiple skills
9. **No web UI** - CLI only
10. **No community norms** - No shared evaluation standards

---

## Improvement Roadmap

### Phase 1: References & Automation (Week 1)
- [x] Create all 5 reference files (cli-reference, anti-patterns, edge-cases, failure-patterns, quick-reference) (cli-reference, anti-patterns, edge-cases, failure-patterns, quick-reference)
- [x] Build automated evaluator CLI (`judge_skill.py`)
- [x] Implement scoring engine with all 8 dimensions
- [x] Add batch evaluation mode

### Phase 2: Calibration & Integration (Week 2)
- [x] Create calibration benchmark suite (benchmarks/)
- [x] Integrate with `skill-creator` as quality gate
- [x] Add historical tracking
- [x] Implement skill comparison mode

### Phase 3: Reporting & Standards (Week 3)
- [x] Create evaluation report templates (JSON output)
- [ ] Build web dashboard (future)
- [x] Establish evaluation standards (120-point rubric)
- [x] Add skill certification levels (A+ to F)

### Phase 4: Advanced Features (Week 4)
- [ ] Auto-fix suggestions for common issues
- [ ] Skill health monitoring (post-deploy quality)
- [ ] Integration with skill registry (quality badges)
- [ ] AI-assisted evaluation (pre-score with human review)

---

## Specific Technical Tasks

### Reference Files
```
references/
  cli-reference.md           # Step 1-5 evaluation protocol, report template
  anti-patterns.md           # Expert anti-patterns with reasoning (for D3)
  edge-cases.md              # Edge cases for knowledge delta evaluation (for D1)
  failure-patterns.md        # Common skill failures (for D5 progressive disclosure)
  quick-reference.md         # Checklist for final report generation
```

### Automated Evaluator
```python
# scripts/judge_skill.py
class SkillJudge:
    DIMENSIONS = [
        ("D1", KnowledgeDeltaEvaluator, 20),
        ("D2", MindsetProcedureEvaluator, 15),
        ("D3", AntiPatternEvaluator, 15),
        ("D4", SpecComplianceEvaluator, 15),
        ("D5", ProgressiveDisclosureEvaluator, 15),
        ("D6", FreedomCalibrationEvaluator, 15),
        ("D7", PatternRecognitionEvaluator, 10),
        ("D8", PracticalUsabilityEvaluator, 15),
    ]
    
    def __init__(self, skill_path: Path):
        self.skill_path = skill_path
        self.skill_content = self.load_skill()
        self.references = self.load_references()
    
    def evaluate(self) -> EvaluationResult:
        scores = {}
        details = {}
        
        for dim_id, evaluator_class, max_score in self.DIMENSIONS:
            evaluator = evaluator_class(self.skill_content, self.references)
            score, detail = evaluator.evaluate()
            scores[dim_id] = score
            details[dim_id] = detail
        
        total = sum(scores.values())
        return EvaluationResult(
            skill_path=self.skill_path,
            scores=scores,
            total=total,
            max_total=120,
            percentage=total/120*100,
            details=details,
            grade=self.grade(total),
            recommendations=self.generate_recommendations(scores, details)
        )
    
    def grade(self, total: int) -> str:
        if total >= 100: return "A+ (Expert)"
        elif total >= 90: return "A (Strong)"
        elif total >= 80: return "B+ (Good)"
        elif total >= 70: return "B (Adequate)"
        elif total >= 60: return "C (Needs Work)"
        else: return "F (Insufficient)"
```

### Calibration Benchmarks
```python
# benchmarks/
CALIBRATION_SKILLS = {
    "expert": ["docx", "xlsx", "pdf", "code-reviewer"],      # Should score 90+
    "strong": ["project-planner", "skill-creator", "skill-judge"],  # 80-90
    "adequate": ["brainstorming", "dynamic-context-pruning"], # 70-80
    "needs_work": ["chinese-translator", "cybersecurity-copilot"], # <70
    "insufficient": ["master-of-dissent", "rap-writer"]       # <60
}

def calibrate(judge: SkillJudge) -> CalibrationReport:
    results = {}
    for category, skills in CALIBRATION_SKILLS.items():
        for skill in skills:
            result = judge.evaluate_skill(skill)
            results[skill] = result
    
    # Verify ranking matches expectations
    # Calculate judge accuracy
    return CalibrationReport(results=results, accuracy=...)
```

### Skill-Creator Integration
```python
# In skill-creator evaluation loop
def quality_gate(skill_path: Path) -> QualityGateResult:
    judge = SkillJudge(skill_path)
    result = judge.evaluate()
    
    if result.total < 70:  # Minimum threshold
        return QualityGateResult(
            passed=False,
            message=f"Skill quality below threshold: {result.total}/120 ({result.grade})",
            details=result.details
        )
    
    if result.scores["D1"] < 11:  # Knowledge Delta minimum
        return QualityGateResult(
            passed=False,
            message=f"Insufficient Knowledge Delta: {result.scores['D1']}/20",
            details=result.details
        )
    
    return QualityGateResult(passed=True, score=result.total)
```

### CLI Design
```bash
# skill-judge evaluate --skill ./my-skill --format json
# skill-judge evaluate --skill ./my-skill --format html --output report.html
# skill-judge batch --skills-dir ./skills --output summary.csv
# skill-judge compare --skill-a ./skill1 --skill-b ./skill2
# skill-judge calibrate --benchmarks-dir ./benchmarks
# skill-judge certify --skill ./my-skill --level expert
# skill-judge history --skill ./my-skill --show-trend
```

---

## Acceptance Criteria
- [x] All 5 reference files complete
- [x] CLI evaluates skill quickly
- [x] Calibration benchmarks implemented
- [x] Skill-creator integration blocks <70/120 skills
- [x] Batch evaluation implemented
- [x] Report templates generate professional output
- [x] Comparison mode highlights key differences
- [ ] Web dashboard (future)

---

## Dependencies
- `skill-creator` (quality gate integration)
- `skill-reviewer` (peer review alignment)
- `collaborative-skill-engineering` (workflow integration)
- `writing-skills` (documentation standards)
- `code-quality` (script validation)
- `verification-before-completion` (evaluation claims)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Evaluator bias | Medium | High | Calibration benchmarks, multiple evaluators |
| Reference drift | Low | Medium | Versioned references, automated checks |
| False negatives | Medium | High | Minimum thresholds, appeal process |
| Gaming the metric | Low | Medium | Hidden test cases, behavioral eval |

---

## Success Metrics
- Evaluation accuracy (vs human): >90% agreement
- Skill quality improvement: +15 points avg after gate
- Calibration stability: <5 point variance across runs
- Adoption: Used in >80% of new skill creations
- Certification: 10+ skills certified expert