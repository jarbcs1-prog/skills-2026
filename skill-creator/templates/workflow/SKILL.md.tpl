---
name: {{name}}
description: {{description}}
---

# {{name}}

{{description}}

## When to use

Trigger this skill when the user needs a defined multi-step process executed reliably and in order — operations, releases, onboarding, procedures.

## Working

1. Read the full procedure in `references/` before starting.
2. Execute steps strictly in order; do not skip validation or checkpoint steps.
3. Record state at each stage so progress is always known.
4. If a step fails, stop and report rather than improvising around it.
5. Confirm completion against the procedure's exit criteria.

## Output

All steps completed with evidence for each; state recorded at every stage.

## Verification

- [ ] Steps executed in documented order
- [ ] State recorded at each checkpoint
- [ ] Failures stopped and reported, not papered over
- [ ] Exit criteria confirmed
- [ ] `references/` consulted when relevant

## Resources

- `scripts/` — executable helpers for deterministic tasks
- `references/` — additional documentation loaded as needed
- `assets/` — files used in output
- `evals/evals.json` — test cases for this skill
