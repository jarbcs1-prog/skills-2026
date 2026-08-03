# Improvement Plan: having-difficult-conversations

## Current State Assessment

**Tier:** 🟢 Production-Ready (Minor Polish)
**Lines:** 302 | **Version:** 2.0.0

### Strengths
- Comprehensive framework selection guide (SBI, Radical Candor, NVC)
- Detailed preparation template with 10 fields
- 15+ anti-patterns with fixes
- Role-play scaffolding with 5-step practice
- Post-conversation follow-up checklist
- Cultural/remote/org context guidance
- 78 guest insights referenced
- Cross-skill references
- Quick reference card

### Gaps Identified
1. **No interactive tooling** - All manual, no CLI or templates
2. **No conversation templates** - Only frameworks, no filled examples per type
3. **No skill integration automation** - Manual cross-skill references
4. **No outcome tracking** - Can't measure conversation effectiveness
5. **No emotion regulation tools** - No pre-conversation calming techniques
6. **No difficult conversation types catalog** - Only 5 types covered
7. **No escalation pathways** - When to involve HR/mediator
8. **No practice simulator** - Role-play is manual only
8. **No team/organization features** - Individual only
9. **No analytics** - No metrics on conversation quality

---

## Improvement Roadmap

### Phase 1: Tooling & Templates (Week 1)
- [ ] Create CLI with conversation type selection
- [ ] Build filled templates for 10+ conversation types
- [ ] Add preparation template generator (interactive)
- [ ] Create conversation script exporter (PDF, markdown)

### Phase 2: Practice & Simulation (Week 2)
- [ ] Build role-play simulator (AI plays other person)
- [ ] Add emotion regulation exercises (breathing, grounding)
- [ ] Implement reaction prediction (likely responses)
- [ ] Create practice session recorder

### Phase 3: Tracking & Analytics (Week 3)
- [ ] Add conversation outcome logging
- [ ] Implement effectiveness metrics (resolution, relationship, clarity)
- [ ] Create conversation history with search
- [ ] Add pattern detection (recurring issues, people)

### Phase 4: Team & Organization (Week 4)
- [ ] Add team conversation norms
- [ ] Implement manager coaching mode
- [ ] Create escalation workflow (HR, mediator)
- [ ] Add cultural adaptation profiles

---

## Specific Technical Tasks

### CLI Design
```bash
# difficult-convo prepare --type "performance" --person "Alex" --output prep.md
# difficult-convo template --type "termination" --format markdown
# difficult-convo practice --type "feedback" --scenario "missed_deadline"
# difficult-convo simulate --persona "defensive" --opening "I need to talk about..."
# difficult-convo log --outcome "resolved" --followup "2026-02-15"
# difficult-convo history --person "Alex" --last 10
# difficult-convo analytics --month 2026-01 --metrics resolution,relationship
```

### Conversation Templates
```markdown
# templates/performance_improvement.md
## Conversation Type: Performance Improvement
## Framework: SBI + Crystal Clear Warning

### Preparation
- **Specific behavior**: [What did camera record?]
- **Impact**: [On team, project, client]
- **Desired outcome**: [Measurable change + timeframe]
- **Warning script**: "I need [behavior] to change. Here's what I expect: [concrete]. We have [timeframe]. If not, we'll have to part ways."

### Conversation Flow
1. **Opening** (Radical Candor): "I care about your growth AND I need to address something directly."
2. **SBI**: Situation → Behavior → Impact
3. **Pause**: Let them respond. "What did you hear me say?"
4. **Expectation**: Clear, measurable, timebound
5. **Support**: "Here's how I'll help: [resources, check-ins]"
6. **Warning** (if needed): Crystal clear consequences
7. **Close**: "What did you hear me say?" + Next steps

### Common Reactions & Responses
| Reaction | Response |
|----------|----------|
| Defensiveness | "I hear you. Not attacking - want us to work better together." |
| Denial | "What did you hear me say?" |
| Emotional | "This is hard. Let's take a moment." |
| Agreement | "Great. Let's document the plan and check in [date]." |

### Follow-up Template
- [ ] Email summary within 24 hours
- [ ] Check-in scheduled: [date]
- [ ] Support resources provided: [list]
- [ ] My debrief: [15 min reflection]
```

### Role-Play Simulator
```python
# simulator.py
class ConversationSimulator:
    PERSONAS = {
        "defensive": DefensivePersona,
        "denial": DenialPersona,
        "emotional": EmotionalPersona,
        "agreeable": AgreeablePersona,
        "hostile": HostilePersona
    }
    
    def simulate(self, user_opening: str, persona: str, 
                 context: ConversationContext) -> SimulationResult:
        # AI plays the other person
        # Returns: their_response, emotional_state, suggested_next_move
        pass
    
    def practice_session(self, conversation_type: str) -> PracticeSession:
        # Guided practice with feedback
        pass
```

### Outcome Tracking
```python
# tracker.py
class ConversationTracker:
    def log(self, conversation: ConversationLog):
        # Stores: type, person, date, framework, outcome, followup_date
        pass
    
    def get_analytics(self, period: Period) -> ConversationAnalytics:
        return ConversationAnalytics(
            total_conversations=...,
            resolution_rate=...,
            relationship_impact=...,
            clarity_score=...,
            recurring_patterns=...,
            framework_effectiveness=...
        )
```

---

## Acceptance Criteria
- [ ] CLI prepares conversation in <2 min
- [ ] 10+ templates cover 90% of difficult conversations
- [ ] Simulator provides realistic responses >80% accuracy
- [ ] Outcome tracking captures 100% of logged conversations
- [ ] Analytics show actionable patterns
- [ ] Practice mode reduces user anxiety (self-reported)
- [ ] Templates export to PDF/Markdown cleanly

---

## Dependencies
- `ai-self-reflection` (post-conversation processing)
- `stop-slop` (script cleanup)
- `requesting-code-review` (analogous feedback seeking)
- `code-quality` (CLI code)
- `verification-before-completion` (effectiveness claims)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Over-scripting | Medium | High | Templates as scaffolding, not scripts |
| Simulator inaccuracy | Medium | Medium | Multiple personas, user feedback loop |
| Privacy concerns | Low | High | Local storage only, no cloud |
| Cultural misfit | Medium | Medium | Cultural profiles, manual adaptation |

---

## Success Metrics
- Preparation time: <5 min for standard conversations
- User confidence (pre/post): +40% improvement
- Conversation resolution rate: >80%
- Relationship preservation: >90%
- Repeat usage: >60% of users return