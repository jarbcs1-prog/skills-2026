# Anti-Patterns & Edge Cases

Reference material for skill-judge evaluation. Loaded on-demand via decision-prompt triggers.

---

## Expert Anti-Patterns (specific + reason)

NEVER use generic AI-generated aesthetics like:
- Overused font families (Inter, Roboto, Arial)
- Cliched color schemes (particularly purple gradients on white backgrounds)
- Predictable layouts and component patterns
- Default border-radius on everything

## Weak Anti-Patterns (vague, no reasoning)

Avoid making mistakes.
Be careful with edge cases.
Don't write bad code.

## Edge Cases & Failure Scenarios

### Knowledge Delta Edge Cases
- **Partial tutorial contamination**: A skill that is 80% expert but has one "What is X" section — the single redundant section still dilutes the knowledge delta score significantly.
- **Over-activation bias**: Agent knows a concept but the skill's reminder is so verbose it becomes redundant rather than activation.
- **False expert claims**: Content presented as "expert-only" that is actually common knowledge (e.g. "always handle errors" is generic, not expert).

### Anti-Pattern Edge Cases
- **Context-dependent anti-patterns**: An anti-pattern that is valid in one domain but not another (e.g. rigid procedures are anti-patterns for creative tasks but required for file-format operations).
- **Evolving anti-patterns**: What was once an expert anti-pattern becomes common knowledge (e.g. "always use HTTPS" is now baseline, not expert).
- **Cultural anti-patterns**: Aesthetic anti-patterns that vary by region or audience (e.g. color symbolism differences).

### Specification Edge Cases
- **Multi-skill overlap**: When multiple skills could apply, the description must disambiguate clearly — vague descriptions cause activation conflicts.
- **Version drift**: Description mentions capabilities that the current skill version doesn't actually support.
- **Keyword stuffing**: Descriptions overloaded with keywords lose specificity and become invisible to the agent.

### Progressive Disclosure Edge Cases
- **Circular references**: Reference A loads Reference B which loads Reference A — causes infinite loops.
- **Stale references**: External reference files updated but SKILL.md triggers not updated to match.
- **Over-triggering**: Every workflow step has a "MANDATORY READ" — causes loading fatigue and irrelevant content.

### Freedom Calibration Edge Cases
- **Hybrid tasks**: Tasks that are partially creative and partially fragile — requires mixed freedom levels within the same skill.
- **Recovery procedures**: High-freedom creative tasks that need low-freedom recovery steps when things go wrong.
- **Tool-specific constraints**: A creative task using a fragile tool — freedom must adapt to the tool's fragility.

## The Meta-Question

When evaluating any Skill, always return to this fundamental question:

> **"Would an expert in this domain, looking at this Skill, say:**
> **'Yes, this captures knowledge that took me years to learn'?"**

If the answer is yes → the Skill has genuine value.
If the answer is no → it's compressing what agent already knows.
