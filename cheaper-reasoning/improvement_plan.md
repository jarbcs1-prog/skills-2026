# Improvement Plan: cheaper-reasoning

## Current State Assessment

**Tier:** 🟠 Functional but Thin (Needs Substantial Expansion)
**Lines:** 100 | **Version:** 1.0 (implied)

### Strengths
- Clear contemplation format with XML tags
- Minimum 10,000 character requirement enforces depth
- Natural thought flow guidelines with examples
- Progressive building patterns
- Explicit anti-conclusion forcing
- Language matching requirement

### Gaps Identified
1. **No validation of contemplation quality** - Length ≠ quality
2. **No integration with other skills** - Standalone reasoning mode only
3. **No tooling support** - Manual format compliance
4. **No examples of good vs bad contemplation**
5. **No convergence detection** - When to stop contemplating
6. **No token budget management** - 10k chars may exceed context
7. **No skill trigger conditions** - When to invoke this vs normal reasoning

---

## Improvement Roadmap

### Phase 1: Quality Validation (Week 1)
- [ ] Add contemplation quality rubric (coherence, progression, self-correction, insight density)
- [ ] Implement automated quality scoring for contemplation output
- [ ] Add convergence detection heuristics (repetition, stabilization, insight saturation)
- [ ] Create good/bad contemplation examples library

### Phase 2: Tooling (Week 2)
- [ ] Create CLI wrapper for reasoning sessions
- [ ] Add token budget enforcement with progressive summarization
- [ ] Implement contemplation checkpointing (save/resume)
- [ ] Add reasoning trace export for analysis

### Phase 3: Integration (Week 3)
- [ ] Define clear trigger conditions (complexity threshold, uncertainty level)
- [ ] Add integration with `systematic-debugging` for root cause analysis
- [ ] Add integration with `brainstorming` for design exploration
- [ ] Create reasoning mode selector (quick/standard/deep)

### Phase 4: Advanced Features (Week 4)
- [ ] Add multi-perspective reasoning (devil's advocate, user persona, expert panel)
- [ ] Implement reasoning pattern library (first principles, analogy, inversion)
- [ ] Add collaborative reasoning (multiple agents with synthesis)
- [ ] Create reasoning effectiveness metrics

---

## Specific Technical Tasks

### Quality Rubric
```python
# reasoning_quality.py
class ContemplationQuality:
    COHERENCE_WEIGHT = 0.25      # Logical flow, no contradictions
    PROGRESSION_WEIGHT = 0.25    # Building on previous thoughts
    SELF_CORRECTION_WEIGHT = 0.25 # Backtracking, revision visible
    INSIGHT_DENSITY_WEIGHT = 0.25 # Novel insights per 1000 chars
    
    def score(self, contemplation: str) -> QualityScore:
        # Analyze structure, repetition, insight markers
        pass
```

### Convergence Detection
```python
# convergence.py
def detect_convergence(contemplation_history: List[str]) -> ConvergenceSignal:
    # Check: last 3 segments similar themes
    # Check: revision rate dropping
    # Check: new insight rate < threshold
    # Return: CONTINUE | CONVERGING | CONVERGED | STALLED
```

### CLI Wrapper
```bash
# cheaper-reasoning think --topic "architecture decision" \
#   --mode deep --budget 15000 --checkpoint reasoning.json
# cheaper-reasoning resume --checkpoint reasoning.json
# cheaper-reasoning analyze --trace reasoning.json --quality
```

### Trigger Conditions
```python
# triggers.py
def should_use_deep_reasoning(task: Task) -> bool:
    return any([
        task.complexity_score > 0.7,
        task.uncertainty_level > 0.6,
        task.requires_architecture_decision,
        task.has_conflicting_constraints,
        task.user_explicitly_requested_reasoning
    ])
```

---

## Merge Consideration

**Potential merge with `systematic-debugging` and `brainstorming`** as reasoning modes:
- Quick reasoning → normal operation
- Standard reasoning → brainstorming exploration
- Deep reasoning → cheaper-reasoning (this skill)
- Debugging reasoning → systematic-debugging

### If Merged
1. Create unified `reasoning-framework` skill with mode selector
2. Each mode has appropriate depth/budget/triggers
3. Shared quality validation and convergence detection
4. Single integration point for other skills

---

## Acceptance Criteria
- [ ] Quality rubric correlates with human judgment >0.8
- [ ] Convergence detection reduces token usage 30% without quality loss
- [ ] CLI wrapper handles 100% of reasoning workflows
- [ ] Trigger conditions correctly classify 90%+ of tasks
- [ ] Integration examples work end-to-end
- [ ] Token budget never exceeded

---

## Dependencies
- `systematic-debugging` (debugging reasoning mode)
- `brainstorming` (design reasoning mode)
- `code-quality` for CLI code
- `verification-before-completion` for quality claims

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Over-reasoning on simple tasks | High | Medium | Strict trigger conditions, quick mode default |
| Token budget overflow | Medium | High | Progressive summarization, hard cap |
| Quality rubric gaming | Low | Medium | Multi-dimensional, human validation |
| Analysis paralysis | Medium | High | Convergence detection, time budgets |

---

## Success Metrics
- Reasoning quality score: avg >0.75/1.0
- Token efficiency: 30% reduction vs unguided
- Appropriate trigger rate: >90% precision/recall
- User satisfaction with reasoning output: >4/5
- Integration adoption: used by >3 other skills