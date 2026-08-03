---
name: {{name}}
description: {{description}}
---

# {{name}}

{{description}}

## When to use

Trigger this skill when the user wants code, documents or configurations audited — reviews, audits, inspections, assessments.

## Working

1. Confirm the review scope and any focus areas.
2. Inspect the target systematically; consult `references/` for the checklist.
3. For each issue record evidence (file:line), severity and a fix suggestion.
4. Distinguish blocking issues from style nits.
5. Deliver a prioritized report, not a vague summary.

## Output

A prioritized review report with findings, evidence, severity and concrete fix suggestions.

## Verification

- [ ] Findings include evidence (file:line where applicable)
- [ ] Issues are prioritized by severity
- [ ] Blocking vs non-blocking clearly distinguished
- [ ] Fix suggestions are actionable
- [ ] `references/` consulted when relevant

## Resources

- `scripts/` — executable helpers for deterministic tasks
- `references/` — additional documentation loaded as needed
- `assets/` — files used in output
- `evals/evals.json` — test cases for this skill
