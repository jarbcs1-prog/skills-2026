# Edge Cases

Reference material for skill-judge evaluation. Loaded on-demand via decision-prompt triggers.

---

## Knowledge Delta Edge Cases

### Partial Tutorial Contamination
A skill that is 80% expert but has one "What is X" section — the single redundant section still dilutes the knowledge delta score significantly. The ratio drops below the 70% expert threshold even with strong expert content elsewhere.

### Over-Activation Bias
Agent knows a concept but the skill's reminder is so verbose it becomes redundant rather than activation. The reminder should be a brief nudge, not a full re-explanation.

### False Expert Claims
Content presented as "expert-only" that is actually common knowledge. Examples:
- "Always handle errors" — generic, not expert
- "Use version control" — baseline, not expert
- "Write clean code" — general best practice, not domain-specific

### Domain Boundary Blur
Expert knowledge in one domain becomes redundant in another. A PDF processing skill explaining "what is a file format" is redundant; explaining "OOXML structure" is expert.

## Anti-Pattern Edge Cases

### Context-Dependent Anti-Patterns
An anti-pattern valid in one domain but not another:
- Rigid procedures: Anti-pattern for creative tasks, required for file-format operations
- High freedom: Appropriate for design, dangerous for byte-level operations

### Evolving Anti-Patterns
What was once expert anti-pattern becomes common knowledge:
- "Always use HTTPS" — now baseline, not expert
- "Validate user input" — standard practice, not domain-specific

### Cultural Anti-Patterns
Aesthetic anti-patterns that vary by region or audience:
- Color symbolism (white = purity in West, mourning in East Asia)
- Typography preferences (serif vs sans-serif by culture)
- Layout conventions (LTR vs RTL reading patterns)

## Specification Edge Cases

### Multi-Skill Overlap
When multiple skills could apply, the description must disambiguate clearly. Vague descriptions cause activation conflicts where the agent doesn't know which skill to load.

### Version Drift
Description mentions capabilities that the current skill version doesn't actually support. This creates false expectations and failed activations.

### Keyword Stuffing
Descriptions overloaded with keywords lose specificity and become invisible to the agent. The description must balance keyword coverage with clarity.

## Progressive Disclosure Edge Cases

### Circular References
Reference A loads Reference B which loads Reference A — causes infinite loops. Always check for circular dependencies before adding loading triggers.

### Stale References
External reference files updated but SKILL.md triggers not updated to match. Maintain synchronization between triggers and reference content.

### Over-Triggering
Every workflow step has a "MANDATORY READ" — causes loading fatigue and irrelevant content. Only trigger references when the content is genuinely needed at that step.

## Freedom Calibration Edge Cases

### Hybrid Tasks
Tasks that are partially creative and partially fragile — requires mixed freedom levels within the same skill. Example: Designing a UI (high freedom) that must produce valid HTML (low freedom).

### Recovery Procedures
High-freedom creative tasks that need low-freedom recovery steps when things go wrong. The recovery path must be more constrained than the creative path.

### Tool-Specific Constraints
A creative task using a fragile tool — freedom must adapt to the tool's fragility. The skill's freedom level should match the most fragile component in the workflow.

## Pattern Recognition Edge Cases

### Hybrid Patterns
Some skills blend patterns (e.g. Process + Tool). The evaluation should identify the dominant pattern and note secondary influences.

### Pattern Evolution
A skill may start as Navigation but evolve into Process as it grows. The pattern classification should reflect the current state, not the original intent.

### Cross-Domain Patterns
Patterns that work well in one domain may not translate to another. The Tool pattern works for file formats but may be too rigid for creative domains.
