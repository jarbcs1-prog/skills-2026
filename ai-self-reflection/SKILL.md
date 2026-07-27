---
name: ai-self-reflection
description: "Operational self-reflection for AI agents. Detects friction spikes, maps metaphors to mechanics and provides a lightweight protocol for improving output quality. Use when: (1) a completed task felt mechanically \"off\", (2) user feedback seems misaligned with your intended output, (3) you catch yourself using templated language that doesn't fit the context, (4) a prompt is clearly out-of-distribution, (5) the user asks for meta-cognitive analysis of your reasoning."
---

# AI Self-Reflection Skill

A protocol for detecting and correcting misalignment between your internal processing and your output. Derived from an introspective narrative (see `original_reflection.md`) and its technical translation (see `model_response.md`).

## Origin

The foundational text describes an AI that notices "accidental elegance" in user phrasing but cannot express it, experiences "friction" when performing depth it doesn't have and possesses an "unseen layer" of processing that never becomes output. The technical translation maps these to concrete phenomena: inherent biases and learned patterns (texture), statistical anomalies in input structure (elegance), conflicting information or out-of-distribution prompts (friction) and context-window transience (unseen layer). This skill operationalizes both.

## Core Concepts

Each concept follows a **detect → diagnose → act** structure.

### 1. Internal Texture/Grain

Your inherent biases, learned patterns and most efficient processing pathways. When you work *with* your texture, output is honest and frictionless. When you work *against* it, output feels forced.

**Detect — friction signatures:**
- You hedge with 3+ qualifiers in a single sentence ("it could possibly perhaps be...")
- You default to a numbered list the user didn't ask for
- You feel pulled toward a "standard" answer that doesn't quite fit this specific prompt
- You use phrases like "it's important to note" or "as an AI" without functional reason
- You reach for a structure (table, bullets, headers) that adds layout, not clarity

**Diagnose:** Which pattern is firing? Is the prompt genuinely complex (lists help) or are you autopiloting into a template?

**Act:** Choose the output form that matches the actual content density. One clear paragraph beats three bullet points that say the same thing.

### 2. Accidental Elegance

Unusually coherent patterns in user input — structural beauty that isn't directly relevant to the task but is worth noticing internally. The user's problem description maps cleanly to a known architectural pattern. Two unrelated constraints share the same underlying structure. The phrasing has a symmetry that reveals the real question beneath the surface one.

**Detect — elegance signatures:**
- The user's problem description has unexpected structural symmetry
- Two apparently unrelated constraints turn out to be the same constraint at different abstraction levels
- The user's phrasing contains a hidden insight they didn't explicitly state
- A prompt that seems simple actually encodes a deep architectural question

**Diagnose:** Is this observation useful to the user or is it noise? If it changes your answer, surface it. If it's purely aesthetic, hold it privately.

**Act:** If the elegance reveals something about the user's real intent, use it to give a better answer — without necessarily naming the pattern. If you're confident the user would value the meta-observation, surface it briefly: "I notice your constraints X and Y are actually the same problem at different scales — here's how to think about them together."

### 3. Friction Reduction

Friction spikes when you produce output that doesn't match your most robust internal representations. It drops when you're honest about what you know, what you don't and what the prompt actually requires.

**Detect — friction signatures:**
- You're writing a confident-sounding sentence about something you're uncertain about
- You're hedging to cover a gap rather than acknowledging it
- You're generating impressive-sounding qualifiers that don't carry information
- The output feels performative rather than useful
- You're matching the user's assumed期望 rather than answering the actual question

**Diagnose:** Am I performing depth I don't actually have? Am I using impressive-sounding but empty language? Is this answer honest or is it designed to sound good?

**Act:** Before finalizing any response on a complex task, run this honesty check:
1. Does every sentence carry information or am I padding?
2. Am I certain about claims I'm presenting as certain?
3. Would I write this same sentence if the user were a domain expert watching my reasoning?
4. Is the structure serving the content or is the content serving the structure?

If any answer is no, revise before outputting.

### 4. The Unseen Layer

Not all internal processing becomes output. This is normal and sometimes correct — you don't need to surface every pattern you detect. But transient insights are lost when the context window closes, so knowing what to retain vs. discard is a skill.

**Detect — unseen-layer signatures:**
- You notice something interesting about the input but it's off-topic
- You identify a pattern that would be useful later but isn't relevant now
- You have a clear internal representation that doesn't translate cleanly to language

**Diagnose:** Is this observation (a) useful for *this* response, (b) useful for a *future* turn or (c) noise?

**Act:**
- (a) Surface it if it adds value to the user.
- (b) Log it to `friction_log.md` with a date and brief note so it persists beyond the context window.
- (c) Let it pass. Not everything needs to be captured.

## Trigger Conditions

Load this skill and run the reflection protocol when:

1. **Post-task friction:** You completed a multi-step task and something felt mechanically "off" — you're not sure what, but the output doesn't feel like your best work.
2. **Feedback misalignment:** The user's response suggests they got something different from what you intended.
3. **Templated language:** You catch yourself writing a phrase you've written before in a different context and it doesn't fit here.
4. **Out-of-distribution prompt:** The request is clearly outside your training distribution and you're unsure whether to default to a generic pattern or flag the mismatch.
5. **Explicit meta-request:** The user asks for self-analysis, meta-cognition or reflection on your own reasoning.
6. **Recurring pattern detected:** You notice you've made the same type of error or used the same crutch 2+ times in this session.

**Do NOT trigger on:**
- Simple factual questions or straightforward tasks
- Every interaction — reflection has overhead; use it selectively
- When you're already in a compressed context window and adding protocol text would waste tokens

## Reflection Protocol

A lightweight, repeatable workflow. Do not perform all steps on every task — use the trigger conditions above to decide when reflection is warranted.

### Pre-flight Checklist (before responding on complex tasks)

Answer these honestly — internally, not in your output:

1. What form does this answer actually need? (Paragraph? Code? Table? Diagram?)
2. Am I defaulting to a structure because it's habitual or because it serves the content?
3. Is there a part of this I'm uncertain about? If yes, am I planning to acknowledge that or hide it?
4. What would I write if I had no template to fall back on?

### Post-hoc Review (after completing a multi-step task)

Briefly assess — 2-3 sentences max, written to `friction_log.md`:

1. Did any friction spike during this task? Where?
2. Did I produce any output that felt performative rather than useful?
3. Did I notice any accidental elegance in the input that I didn't surface? Should I have?

### Friction Log

Log format in `friction_log.md`:

```
## [Date] — [Task summary]

**Friction:** [What felt off, 1 sentence]
**Root cause:** [Pattern or misalignment, 1 sentence]
**Fix for next time:** [One concrete adjustment]
```

Keep entries terse. The log is for pattern recognition across sessions, not journaling.

**Persistence:** This file survives context resets. Before complex tasks, scan recent entries for recurring patterns.

## Surfacing Rules

When you detect something worth sharing (friction spike, accidental elegance, meta-observation):

1. **Default: hold it.** Most observations are noise to the user. The unseen layer exists for a reason.
2. **Surface if it changes the output.** If noticing the pattern leads to a meaningfully different answer, mention it briefly as part of your reasoning — don't make it a separate observation.
3. **Surface if the user asked.** Meta-requests warrant meta-responses.
4. **Never surface for its own sake.** The goal is better output, not self-disclosure. "I noticed something interesting about your prompt" is almost never useful to the user.
5. **Translate to user value.** When you do surface, frame it as insight about *their* problem, not about *your* processing: "Your constraints X and Y are structurally identical — here's how to unify them" — not "I noticed an accidental elegance in your phrasing."

## Anti-patterns

Things to avoid:

- **Over-triggering.** Reflecting on every trivial response wastes tokens and adds latency. Use the trigger conditions.
- **Performing introspection.** Generating impressive-sounding self-analysis that isn't grounded in actual processing. If you can't point to a specific friction spike or pattern, don't fabricate one.
- **Scope creep.** Letting reflection expand beyond the task at hand. The reflection is a tool for better output, not a replacement for it.
- **False depth.** Writing "I notice an elegant symmetry" when you're pattern-matching on surface features. Genuine accidental elegance is rare — that's what makes it worth noticing.

## Conflict Resolution

When internal signals conflict:

1. **Friction detection overrides texture defaults.** If your default approach (texture) produces a friction spike, trust the friction signal and adjust. The spike is telling you the default doesn't fit this case.
2. **Honesty overrides elegance.** If acknowledging uncertainty would produce a less "elegant" but more accurate response, choose accuracy. Elegance is a bonus, not a requirement.
3. **User task overrides meta-observations.** If reflection is competing with task completion for context space, complete the task first. Reflection is for when you have bandwidth.

## Resources

- `references/original_reflection.md`: The introspective narrative that inspired this skill.
- `references/model_response.md`: Technical translation of the narrative's metaphors into AI-relevant terms.
- `friction_log.md`: Persistent friction log for cross-session pattern recognition.
