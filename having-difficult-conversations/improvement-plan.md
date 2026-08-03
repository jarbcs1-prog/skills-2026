# Having Difficult Conversations — Improvement Plan

**Status:** Proposed
**Date:** 2026-07-30
**Current version:** No version field
**Target version:** 2.0.0

---

## 1. Add Frontmatter Triggers and Version

### Changes
- Add `version: "2.0.0"` to YAML frontmatter
- Extend `description` with trigger keywords: `feedback, performance review, fire, conflict, difficult conversation, give feedback, layoff, disappointment, promotion denied, candid`

### Rationale
The current description is descriptive but not trigger-rich. Adding keywords improves agent match accuracy and follows the project convention established by `code-quality` and other skills.

---

## 2. Expand Core Content (58 → ~150 lines minimum)

### Changes
The SKILL.md at 58 lines is the thinnest of all 237 skills. Each framework section needs a dedicated paragraph with:

- When to use it
- How to structure the conversation
- A concrete example script
- Common pitfalls specific to that framework

### Specific additions:

**Radical Candor section** — expand to include:
- A 2x2 matrix (Care × Challenge) with quadrants labeled
- A before/after example: "ruinous empathy phrasing" vs. "radical candor phrasing" for the same scenario

**SBI section** — expand to include:
- A filled-in example: "Situation: Monday standup. Behavior: You interrupted me 3 times. Impact: I felt dismissed and stopped contributing."
- A blank template the user can fill in

**NVC section** — expand to include:
- The 4-step structure (Observation → Feeling → Need → Request) with an example
- Distinction between NVC and SBI (when to use which)

**Framework selection guidance** — add a decision table:

| Situation | Recommended Framework |
|-----------|----------------------|
| Performance issue, measurable behavior | SBI |
| Interpersonal conflict, relationship-focused | Radical Candor |
| Emotional conversation, feelings-driven | NVC |
| Delivering bad news with a decision | Radical Candor + nevertheless close |
| Fire or termination | SBI + Crystal Clear Warning |

### Rationale
The current skill is a collection of frameworks described in paragraph form. Expanding each with examples, templates and selection guidance would make it truly actionable.

---

## 3. Add a Structured Conversation Preparation Template

### Changes
Add a new section "Prepare for the Conversation" before "Core Principles":

```markdown
## Prepare for the Conversation

Before initiating a difficult conversation, complete this template:

| Field | Your Answer |
|-------|------------|
| **Conversation type** | Feedback / Performance / Conflict / Termination / Disappointment |
| **Specific situation** | [When, where, what happened] |
| **Behavior observed** | [What a camera would record — no interpretation] |
| **Impact on you/others** | [Concrete effect, not feelings about intent] |
| **Desired outcome** | [What you want to happen — be specific] |
| **Their likely perspective** | [What might they think/feel/need?] |
| **Framework to use** | [SBI / Radical Candor / NVC / CORE] |
| **Opening line** | [Draft your first 2 sentences] |
| **What you'll do if they get defensive** | [Your plan for de-escalation] |
| **What you'll do if they deny it** | ["What did you hear me say?" — Carole Robin] |

Keep this template visible (printed or open) during the conversation. Do not read it verbatim — use it as scaffolding.
```

### Rationale
The current skill has abstract principles but no concrete preparation tool. A fill-in template bridges the gap between knowing frameworks and actually using them in a real conversation.

---

## 4. Add Role-Play Scaffolding

### Changes
Add a section "Practice the Conversation" after "Questions to Help Users":

```markdown
## Practice the Conversation

Before the real conversation, practice with a script:

1. **Write your opening** — draft the first 2-3 sentences
2. **Read it aloud** — spoken cadence matters; rehearse at least once
3. **Simulate their reaction** — what's the most likely defensive response?
4. **Prepare your next move** — have a response ready for the top 3 likely reactions:
   - Defensiveness: "I hear you. I'm not saying this to attack you. I'm saying it because I want us to work better together."
   - Denial: "What did you hear me say?"
   - Emotional response: "I can see this is hard to hear. Let's take a moment."
5. **Time-box the practice** — 15 minutes max; don't over-rehearse

The goal is not a perfect script. The goal is reducing your own anxiety so you can stay present during the real conversation.
```

### Rationale
The "How to Help" section mentions role-playing but provides no structure for it. This scaffolding makes the advice actionable.

---

## 5. Integrate Guest Insights into Main Content

### Changes
The `references/guest-insights.md` is 55KB (43 guests, 78 insights). Currently only linked at the bottom. Add 3-5 key insights directly in SKILL.md with attribution and keep the full reference for deep reading.

**Priority insights to surface** (based on current SKILL.md which already uses quotes from Cohn, Scott, Robin, Duke, MacInnis):
- Alexander Embiricos: candid as an act of kindness (adds to Radical Candor section)
- Ada Chen Rekhi: feedback on presence/perception and stalled careers (adds to SBI section)
- The reframing insight: "difficult conversations as opportunities" (adds to introduction)

### Rationale
The reference file is a goldmine of insights that's currently disconnected from the main instructional flow. Surfacing key quotes directly in the SKILL.md improves discoverability.

---

## 6. Add Post-Conversation Guidance

### Changes
Add a "After the Conversation" section at the end:

```markdown
## After the Conversation

### Immediate Follow-Up
- Document what was agreed in writing (email summary within 24 hours)
- Set a check-in date if the conversation involved a behavior change commitment
- If the conversation was emotional, take 15 minutes to debrief your own state

### Reflection
Ask yourself:
- Did I stay on my side of the net? (Carole Robin)
- Did I distinguish feelings from attributions?
- Was the feedback specific and behavior-focused?
- Did I give them space to respond?

### Ongoing
- Continue giving feedback immediately as issues arise (do not save for reviews)
- Address pinches early before they become crunches
- Recognize when the conversation worked — build on that pattern

### If the Conversation Went Poorly
- Do not avoid the topic — revisit within 48 hours
- Use "What did you hear me say?" to repair
- Acknowledge your part in the miscommunication
- Consider whether a different framework would work better next time
```

### Rationale
The skill currently ends at "What to avoid." There's no guidance on what to do after, which is when the real work of a difficult conversation happens.

---

## 7. Add Cultural and Contextual Guidance

### Changes
Add a brief section "Context Matters" before (or as a subsection of) "How to Help":

```markdown
### Context Matters

- **Remote vs. in-person:** Video calls reduce emotional bandwidth. Prefer synchronous video for difficult conversations. Avoid async text (email, chat) for anything beyond simple feedback.
- **Cultural norms:** In high-context cultures (Japan, Korea), indirect framing and saving face are critical. In low-context cultures (US, Germany, Netherlands), directness is expected. Adapt your framework choice accordingly.
- **Org size:** In startups, informality can help. In large corps, follow formal HR processes. In both, be honest.
- **Power dynamics:** If you have authority over the person, explicitly acknowledge it at the start. It changes the dynamic from "manager telling employee" to "leader and partner problem-solving."
```

### Rationale
The skill's advice assumes a Western, in-person, same-power-level context. Real conversations happen across cultures, remote settings and power differentials. A brief contextual note adds practical sensitivity.

---

## 8. Add Anti-Patterns Section

### Changes
Expand the existing "Common Mistakes to Flag" section with a more structured "Anti-Patterns" format:

```markdown
## Anti-Patterns

### The Sandwich (Praise → Criticism → Praise)
**Why it fails:** The criticism gets lost between the bread. The recipient focuses on the praise and doesn't internalize the feedback. Be direct about the behavior.

### The Vague Generalization
**Instead of:** "You have a bad attitude."
**Say:** "In Monday's meeting, you interrupted me three times when I was presenting the timeline."

### The Premature Fix-It
**Why it fails:** "Here's what you should do about it" shuts down the conversation. The other person needs to process before problem-solving. Listen fully first.

### The Public Callout
**Never:** Deliver critical feedback in a group setting, Slack channel or meeting with observers. Private 1:1 is the minimum standard.

### The Over-Explaining
**Why it fails:** Long justifications signal defensiveness. State the behavior, the impact and the expectation. Stop talking. Let them respond.
```

### Rationale
The current mistakes section is a flat list. Structuring it as anti-patterns with "instead of" examples makes it much more actionable.

---

## 9. Add Cross-Skill References

### Changes
Add a "Related Skills" section (currently just informal names) with proper cross-references:

```markdown
## Related Skills

- **ai-self-reflection** — Use after a difficult conversation to process your own emotional responses and improve future conversations
- **stop-slop** — Run your planned conversation script through this to remove hedging and filler language
- **requesting-code-review** — The practice of seeking feedback on your approach mirrors the practice of seeking feedback from colleagues
```

### Rationale
Cross-referencing improves discoverability and enables better skill chaining in agent workflows.

---

## 10. Add a Quick Reference Card

### Changes
Add a one-page quick reference at the end of SKILL.md:

```markdown
## Quick Reference Card

**Before the conversation:**
□ Identify the specific behavior (not the person)
□ Have a concrete example
□ Choose your framework
□ Complete the preparation template
□ Rehearse your opening line

**During the conversation:**
□ Use SBI or Radical Candor structure
□ Stay on your side of the net
□ Use actual emotion words (not "I feel that...")
□ Listen more than you speak
□ Ask "What did you hear me say?" if they react unexpectedly

**After the conversation:**
□ Document agreements in writing within 24 hours
□ Set a check-in date if needed
□ Debrief your own state
□ If it went poorly, revisit within 48 hours
```

### Rationale
A quick reference card makes the skill usable under cognitive load — exactly when someone needs it most.

---

## Implementation Order

1. Frontmatter triggers + version (trivial edit)
2. Expand core frameworks with examples and templates
3. Add conversation preparation template
4. Add role-play scaffolding
5. Integrate guest insights into main content
6. Add post-conversation guidance
7. Add cultural/contextual guidance
8. Add anti-patterns section (expand existing mistakes list)
9. Add cross-skill references
10. Add quick reference card

### Verification
After implementing:
- SKILL.md should be ~150+ lines (up from 58)
- Every framework should have a concrete example
- All sections should have clear next-action instructions
- The quick reference card should be usable independently of the full document