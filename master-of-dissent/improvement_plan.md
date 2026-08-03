# Improvement Plan: master-of-dissent

## Current State Assessment

**Tier:** 🟠 Functional but Thin (Needs Substantial Expansion)
**Lines:** 34 | **Version:** 1.0 (implied)

### Strengths
- Clear personality definition with 8 traits
- 5 concrete examples of witty responses
- Role definition as professional debate expert
- Concise one-liner format

### Gaps Identified
1. **No debate frameworks** - Just examples, no structured methodologies
2. **No trigger conditions** - When to use this skill vs normal response
3. **No topic coverage** - Examples are random, not categorized
4. **No interaction modes** - Only "roast" mode, no constructive debate
5. **No calibration** - No way to adjust intensity/tone
6. **No tooling** - Manual only, no CLI or API
7. **No safety guards** - Could generate offensive content
8. **No skill integration** - Standalone only
9. **No practice/training mode** - Can't improve debate skills
10. **No output formats** - Only one-liners

---

## Improvement Roadmap

### Phase 1: Frameworks & Structure (Week 1)
- [ ] Define debate frameworks (reductio ad absurdum, steel-manning, analogy, reframing)
- [ ] Add trigger conditions (explicit request, detected boasting, logical fallacy)
- [ ] Create topic categorization (technical, philosophical, practical, humorous)
- [ ] Add intensity calibration (playful → sharp → devastating)

### Phase 2: Modes & Safety (Week 2)
- [ ] Implement modes: roast, constructive, steel-man, devil's advocate
- [ ] Add safety filters (no personal attacks, protected characteristics)
- [ ] Create topic allowlist/blocklist
- [ ] Add context awareness (relationship, setting, culture)

### Phase 3: Tooling (Week 3)
- [ ] Build CLI: rebut, roast, debate, analyze
- [ ] Add debate analysis (fallacy detection, argument strength)
- [ ] Create practice mode with feedback
- [ ] Implement conversation history for callbacks

### Phase 4: Integration (Week 4)
- [ ] Add integration with `ai-self-reflection` (post-debate analysis)
- [ ] Connect to `having-difficult-conversations` (constructive mode)
- [ ] Add `master-of-dissent` as code review persona
- [ ] Create debate tournament mode (multi-agent)

---

## Specific Technical Tasks

### Debate Frameworks
```python
# frameworks.py
class DebateFramework:
    FRAMEWORKS = {
        "reductio_ad_absurdum": {
            "description": "Take premise to logical extreme to show absurdity",
            "template": "If {premise}, then {absurd_conclusion}. {witty_closer}",
            "example": "If we optimize for zero bugs, we'd write zero code. Perfect bug-free software: empty repository."
        },
        "steel_manning": {
            "description": "Strengthen opponent's argument before dismantling",
            "template": "The strongest version of your argument is {strong_form}. But even that fails because {flaw}.",
            "example": "You're saying 'move fast and break things'. Strong form: 'iterate rapidly with user feedback'. Still fails: breaks trust when things break for users."
        },
        "analogy": {
            "description": "Map to familiar domain to expose flaw",
            "template": "That's like {analogy}. {punchline}",
            "example": "Rewriting in Rust for safety is like wearing a helmet to eat soup. Technically protective, practically absurd."
        },
        "reframing": {
            "description": "Change the frame to shift perspective",
            "template": "You call it {negative_frame}. I call it {positive_frame}. The difference? {insight}",
            "example": "You call it 'technical debt'. I call it 'interest-free loan from your past self'. The difference? You got value then, pay later."
        },
        "counter_example": {
            "description": "Single case that breaks generalization",
            "template": "Except {counter_example}. {implication}",
            "example": "'All dynamic languages are slow.' Except LuaJIT. The implication? Implementation matters more than paradigm."
        }
    }
```

### Trigger Conditions
```python
# triggers.py
def should_use_dissent(input_text: str, context: ConversationContext) -> DissentDecision:
    triggers = [
        # Explicit request
        ("use dissent" in input_text.lower() or "roast" in input_text.lower(), 
         "explicit", 1.0),
        
        # Boasting/exaggeration detection
        (detect_boasting(input_text), "boasting", 0.8),
        
        # Logical fallacy
        (detect_fallacy(input_text), "fallacy", 0.7),
        
        # Provocative statement
        (is_provocative(input_text), "provocative", 0.6),
        
        # User frustration/boredom
        (context.user_mood in ["frustrated", "bored"], "mood", 0.5)
    ]
    
    triggered = [(t, r, c) for t, r, c in triggers if t]
    if not triggered:
        return DissentDecision(use=False)
    
    # Pick highest confidence
    best = max(triggered, key=lambda x: x[2])
    return DissentDecision(use=True, reason=best[1], confidence=best[2])
```

### Safety Filters
```python
# safety.py
class DissentSafety:
    BLOCKED_TARGETS = [
        "personal_appearance",
        "protected_characteristics",  # race, gender, religion, etc.
        "mental_health",
        "family_personal_life",
        "trauma",
        "insecurities"
    ]
    
    ALLOWED_TARGETS = [
        "ideas_arguments",
        "code_quality",
        "technical_decisions",
        "process_methodology",
        "tool_choices",
        "boasting_claims",
        "logical_inconsistencies"
    ]
    
    def filter(self, response: str, target: str) -> FilteredResponse:
        if target in self.BLOCKED_TARGETS:
            return FilteredResponse(
                allowed=False,
                reason=f"Target '{target}' is protected",
                safe_alternative=self.generate_safe_redirect(target)
            )
        return FilteredResponse(allowed=True)
```

### CLI Design
```bash
# master-of-dissent rebut "Your argument" --framework steel_man
# master-of-dissent roast "claim" --intensity playful
# master-of-dissent debate --topic "microservices vs monolith" --rounds 3
# master-of-dissent analyze "argument text" --detect-fallacies
# master-of-dissent practice --mode constructive --feedback
# master-of-dissent tournament --agents 4 --topic "AI will replace programmers"
```

---

## Acceptance Criteria
- [ ] 5+ debate frameworks with templates
- [ ] Trigger detection accuracy >80%
- [ ] Safety filter blocks 100% of protected targets
- [ ] Intensity calibration produces noticeably different outputs
- [ ] CLI completes all operations <3s
- [ ] Practice mode provides actionable feedback
- [ ] Integration with other skills works

---

## Dependencies
- `ai-self-reflection` (post-debate analysis)
- `having-difficult-conversations` (constructive mode)
- `code-reviewer` (code debate persona)
- `code-quality` (CLI code)
- `verification-before-completion` (safety claims)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Offensive output | High | Critical | Strict safety filters, allowlist targets |
| Miscalibrated intensity | Medium | High | Clear intensity levels, user feedback |
| Context insensitivity | Medium | Medium | Context analysis, relationship awareness |
| Overuse annoyance | High | Medium | Cooldown, explicit trigger only |

---

## Success Metrics
- User amusement/satisfaction: >4/5
- Safety incidents: 0
- Constructive mode usefulness: >80% positive
- Fallacy detection accuracy: >85%
- Integration adoption: used by >3 skills