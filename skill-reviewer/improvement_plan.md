# Improvement Plan: skill-reviewer

## Current State Assessment

**Tier:** 🟡 Strong Core (Needs Structure/Polish)
**Lines:** 203 | **Version:** 1.0 (implied)

### Strengths
- Three review modes (self, external, auto-PR)
- Auto-install dependency sequence (skill-creator)
- Clear evaluation checklist (quick + full reference)
- Core principle: Additive only (with examples)
- Common issues with before/after fixes
- PR guidelines with tone guidance
- Self-review checklist (Respect Check)
- References to templates (checklist, PR, marketplace)

### Gaps Identified
1. **Missing reference files** - evaluation_checklist.md, pr_template.md, marketplace_template.json not present
2. **No automated review CLI** - Manual process only
3. **No integration with skill-judge** - Should use as quality gate
4. **No batch review** - Single skill only
5. **No review analytics** - No metrics on review effectiveness
6. **No skill health scoring** - No ongoing quality tracking
7. **No auto-fix suggestions** - Manual fixes only
8. **No cross-skill consistency** - Can't check ecosystem patterns
9. **No review history** - Can't track improvements over time
10. **No collaboration features** - Single reviewer only

---

## Improvement Roadmap

### Phase 1: References & Automation (Week 1)
- [x] Create all 3 reference files (evaluation_checklist.md, pr_template.md, marketplace_template.json)
- [x] Build automated review CLI (cli.py) (`review_skill.py`)
- [x] Integrate `skill-judge` as quality gate
- [x] Add batch review mode

### Phase 2: Intelligence (Week 2)
- [x] Add cross-skill consistency checks
- [x] Implement auto-fix suggestions for common issues
- [x] Add skill health scoring (post-deploy monitoring)
- [x] Create review history tracking

### Phase 3: Collaboration (Week 3)
- [ ] Add multi-reviewer workflow (future)
- [ ] Implement review assignment (future)
- [ ] Add review analytics dashboard (future)
- [x] Review templates in references/

### Phase 4: Ecosystem (Week 4)
- [ ] Integrate with skill registry (future) (quality badges)
- [ ] Add automated PR creation (future) for external skills
- [ ] Implement skill certification workflow (future)
- [ ] Add review performance metrics (future)

---

## Specific Technical Tasks

### Reference Files
```markdown
# references/evaluation_checklist.md
## Comprehensive Skill Evaluation Checklist

### Frontmatter (Required)
- [ ] `name`: lowercase, alphanumeric + hyphens, ≤64 chars
- [ ] `description`: third-person, includes WHAT, WHEN, KEYWORDS
- [ ] `version`: semantic versioning (optional but recommended)

### Instructions
- [ ] Imperative form used throughout
- [ ] SKILL.md body < 500 lines
- [ ] Clear workflow pattern (Mindset/Navigation/Philosophy/Process/Tool)
- [ ] Decision trees for multi-path scenarios
- [ ] Code examples are executable (not pseudocode)
- [ ] Error handling and fallbacks documented
- [ ] Edge cases covered

### Resources
- [ ] No hardcoded absolute paths
- [ ] Scripts have shebang and error handling
- [ ] References have loading triggers (MANDATORY/Do NOT Load)
- [ ] Assets are referenced correctly
- [ ] Tests exist for verifiable outputs

### Progressive Disclosure
- [ ] Layer 1: Metadata only (~100 tokens)
- [ ] Layer 2: SKILL.md body (<300 lines ideal)
- [ ] Layer 3: Resources on demand
- [ ] Clear "MANDATORY - READ ENTIRE FILE" triggers
- [ ] Explicit "Do NOT load" guidance

### Freedom Calibration
- [ ] Task fragility assessed (High consequence → Low freedom)
- [ ] Specificity matches fragility

### Pattern Recognition
- [ ] Follows one official pattern
- [ ] Deviations documented and justified

### Practical Usability
- [ ] Decision trees for multi-path
- [ ] Working code examples
- [ ] Error handling with fallbacks
- [ ] Edge cases covered
- [ ] Immediately actionable
```

### Automated Reviewer
```python
# scripts/review_skill.py
class SkillReviewer:
    def __init__(self, skill_path: Path):
        self.skill_path = skill_path
        self.judge = SkillJudge(skill_path)  # Integrate skill-judge
    
    def review(self, mode: ReviewMode = ReviewMode.SELF) -> ReviewResult:
        if mode == ReviewMode.SELF:
            return self.self_review()
        elif mode == ReviewMode.EXTERNAL:
            return self.external_review()
        elif mode == ReviewMode.AUTO_PR:
            return self.auto_pr_review()
    
    def self_review(self) -> ReviewResult:
        # 1. Run skill-judge evaluation
        judge_result = self.judge.evaluate()
        
        # 2. Run structure validation
        structure_result = self.validate_structure()
        
        # 3. Run security scan
        security_result = self.security_scan()
        
        # 4. Check cross-skill consistency
        consistency_result = self.check_consistency()
        
        # 5. Generate auto-fix suggestions
        fixes = self.generate_fixes(judge_result, structure_result)
        
        return ReviewResult(
            judge=judge_result,
            structure=structure_result,
            security=security_result,
            consistency=consistency_result,
            suggested_fixes=fixes,
            passed=judge_result.total >= 70 and structure_result.passed
        )
    
    def generate_fixes(self, judge_result, structure_result) -> List[FixSuggestion]:
        fixes = []
        # Auto-fix: description format
        if judge_result.scores["D4"] < 14:
            fixes.append(FixSuggestion(
                file="SKILL.md",
                issue="Description missing WHEN/KEYWORDS",
                fix="Rewrite description in third-person with trigger conditions",
                example="Browses YouTube videos and generates summaries. Use when..."
            ))
        # Auto-fix: missing workflow
        if "workflow" not in self.skill_content.lower():
            fixes.append(FixSuggestion(
                file="SKILL.md",
                issue="No workflow pattern detected",
                fix="Add workflow checklist or phased process"
            ))
        return fixes
```

### Batch Review
```bash
# skill-reviewer review --skill ./my-skill --mode self
# skill-reviewer review --skills-dir ./skills --batch --output report.csv
# skill-reviewer review --skill ./external-skill --mode external --pr
# skill-reviewer health --skill ./my-skill --track --period 30d
# skill-reviewer consistency --skills-dir ./skills --report
```

---

## Acceptance Criteria
- [x] 3 reference files complete
- [x] CLI completes self-review in <15s
- [x] Skill-judge integration blocks <70/120 skills
- [x] Auto-fix suggestions implemented of common issues
- [x] Batch review implemented
- [x] Cross-skill consistency checks of pattern violations
- [ ] Auto-PR (future)

---

## Dependencies
- `skill-judge` (quality gate - mandatory integration)
- `skill-creator` (validation scripts)
- `collaborative-skill-engineering` (workflow alignment)
- `writing-skills` (documentation standards)
- `code-quality` (script validation)
- `verification-before-completion` (review claims)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Over-automation | Medium | Low | Human approval required for PRs |
| False fix suggestions | Medium | Medium | Confidence thresholds, manual review |
| Registry API changes | Low | Medium | Versioned API, fallback |

---

## Success Metrics
- Self-review adoption: >90% of skill creators
- Issue detection rate: >95% of skill-judge issues
- Auto-fix acceptance: >70% of suggestions applied
- Review time: <5 min for self-review
- External review quality: >4/5 satisfaction