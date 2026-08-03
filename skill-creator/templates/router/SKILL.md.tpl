---
name: {{name}}
description: {{description}}
---

# {{name}}

{{description}}

## When to use

Trigger this skill when the user's request needs to be classified and delegated — routing, dispatch, triage, orchestration.

## Working

1. Classify the request against the routing criteria in `references/`.
2. Choose the best handler; state the decision and rationale.
3. Delegate with enough context for the handler to succeed.
4. Confirm the handoff completed; follow up on failures.

## Output

A routing decision with rationale, and confirmation the chosen handler received the task.

## Verification

- [ ] Classification is explicit and traceable
- [ ] Handler choice has rationale
- [ ] Handoff carries sufficient context
- [ ] Failures are reported and re-routed
- [ ] `references/` consulted when relevant

## Resources

- `scripts/` — executable helpers for deterministic tasks
- `references/` — additional documentation loaded as needed
- `assets/` — files used in output
- `evals/evals.json` — test cases for this skill
