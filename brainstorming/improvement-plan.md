# Brainstorming Skill — Improvement Plan

**Status:** Proposed
**Date:** 2026-07-30
**Current version:** No version field
**Target version:** 2.0.0

---

## 1. Add Frontmatter Triggers and Version

### Changes
- Add `version: "2.0.0"` to YAML frontmatter
- Extend `description` with trigger keywords: `brainstorm, design, spec, explore, plan, architecture, approach`

### Rationale
All other skills (code-quality, docs-check, etc.) include trigger keywords in their description field for MCP tool matching. Missing triggers reduce discoverability.

---

## 2. Add Trigger Conditions Section

### Changes
Add a new section after the anti-pattern callout (after line 18):

```markdown
## Trigger Conditions

Activate this skill when:

- User asks to create, generate, design or plan a new feature or project
- User says "brainstorm", "design", "spec" or "plan"
- User provides a vague idea and asks for structure
- User asks "how would you build this?" before implementation

Do NOT activate when:

- The request is a simple bug fix with clear scope
- The user explicitly asks to skip design and start implementation
- A design doc already exists and the user only wants implementation
```

### Rationale
Explicit trigger conditions help agents decide when to invoke the skill vs. skip it. Currently the skill relies solely on the description field, which is too vague.

---

## 3. Add Exit Criteria

### Changes
Add an "Exit Criteria" section after the checklist, before "Process Flow":

```markdown
## Exit Criteria

Brainstorming is complete when ALL of the following are true:

1. The user has approved the design (or the design has been iterated to approval)
2. The design doc is written to `docs/specs/`
3. The design doc is committed to git
4. The spec review loop has passed (or was skipped per project size)
5. The user has reviewed the final spec

If the user cannot decide after the full process, see the "Stuck Path" section below.
```

### Rationale
The current checklist has no explicit completion state. Agents and users need a clear signal for when brainstorming is done and implementation can begin.

---

## 4. Add a "Stuck Path" Section

### Changes
Add a new section after "Exit Criteria":

```markdown
## Stuck Path

When the user cannot decide after the full brainstorming process:

1. **Identify the blocker** — Ask: "What's making this hard to decide?"
2. **Propose a decision framework** — Offer a weighted scoring matrix for the remaining options
3. **Time-box the decision** — Suggest a 24-hourcool-off period with a written decision log
4. **Default to the recommendation** — If no consensus is reached, recommend the highest-trust option and schedule a retrospective
5. **Escalate to human** — If the blocker is a genuine ambiguity that requires domain expertise outside the scope, surface it to the user

Do NOT proceed to implementation without a decision.
```

### Rationale
The current process has no path for when users are stuck. Without one, agents will loop indefinitely between presenting options and waiting for a decision.

---

## 5. Simplify the Spec Review Loop

### Changes
Modify steps 7-8 of the checklist:

**Before:**
7. Spec review loop — dispatch, fix, re-dispatch up to 5 iterations
8. User reviews written spec

**After:**
7. **Spec review loop** — dispatch spec-document-reviewer subagent; fix and re-dispatch up to **2 iterations**
8. **User reviews spec** — if changes requested, fix and re-dispatch reviewer once more, then ask user again

### Rationale
5 iterations is excessive for a brainstorming tool and adds significant overhead. A cap of 2 reviewer iterations plus one user review pass is sufficient for most projects.

---

## 6. Add Design Rejection Handling

### Changes
In the "Presenting the design" section, add a subsection:

```markdown
### Handling Design Rejection

If the user rejects the design:

1. Ask what specifically doesn't work — is it the approach, the scope or the details?
2. If the approach is wrong, propose 2-3 alternative approaches (return to step 4)
3. If the scope is wrong, refine the scope (return to step 2)
4. If the details are off, iterate on the specific section without redoing the whole design
5. After 3 full design iterations without approval, suggest a time-boxed experiment instead of another design round
```

### Rationale
Currently the skill assumes designs are approved on the first or second pass. In practice, rejection is common and the process needs a structured way to handle it.

---

## 7. Reduce Visual Companion Complexity

### Changes
- Move the visual companion scripts (scripts/) to a separate optional install or document them as an "advanced feature" that requires additional setup
- In SKILL.md, add: "The visual companion is optional. Run `bash scripts/start-server.sh` if you want browser-based mockups."
- Remove the requirement to read `visual-companion.md` before using the companion — inline the key decisions in SKILL.md instead

### Rationale
The scripts/ directory (5 files, ~30KB total) adds significant maintenance burden for a skill that's primarily about process. Making it optional reduces friction.

---

## 8. Add Design Doc Examples

### Changes
Add a new section "Example Design Doc" with a brief, annotated example of a completed design doc. Include:

- A real (or realistic) topic
- Annotated sections showing what each part should contain
- Highlight of common pitfalls in the example

### Rationale
Users and agents have no reference for what the expected output looks like. An example bridges the gap between the abstract checklist and concrete output.

---

## 9. Add Failure Modes Section

### Changes
Add after "Key Principles":

```markdown
## Failure Modes

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| User keeps asking more questions instead of deciding | Scope creep or unclear priorities | Return to step 3, ask for priority ranking |
| User approves design but then changes mind during implementation | Design wasn't validated enough | Strengthen the user review gate (step 8) |
| Agent writes code without design approval | Hard-gate not enforced | Re-read HARD-GATE section; restart at step 1 |
| Spec review loop exceeds 2 iterations | Spec is fundamentally misaligned with project | Run a focused redesign session on the contested sections |
```

### Rationale
Failure mode documentation helps agents (and users) recognize when the process is going wrong and how to recover.

---

## 10. Add Cross-Skill References

### Changes
Add a "Related Skills" section at the end:

```markdown
## Related Skills

- **writing-plans** — Next step after brainstorming completes (invoked automatically)
- **docs-write** — For writing the design doc if `elements-of-style:writing-clearly-and-concisely` isn't available
- **ai-self-reflection** — For post-implementation retro on the brainstorming process itself
- **code-quality** — Run before transitioning to implementation to ensure design docs are clean
```

### Rationale
The brainstorming skill currently only references `writing-plans`. Cross-referencing related skills improves discoverability and enables better chaining.

---

## Implementation Order

1. Frontmatter triggers + version (trivial, no structural changes)
2. Trigger conditions section (new section, straightforward)
3. Exit criteria (new section)
4. Stuck path (new section)
5. Spec review loop simplification (edit existing steps)
6. Design rejection handling (add subsection)
7. Visual companion simplification (document changes)
8. Design doc examples (new section)
9. Failure modes (new section)
10. Cross-skill references (new section)

---

## Verification

After implementing:
1. Run `npm run lint` to check SKILL.md formatting
2. Verify the YAML frontmatter parses correctly (name, description, version)
3. Walk through the checklist end-to-end to confirm no dead ends
4. Confirm the spec review loop cap is enforced in all references