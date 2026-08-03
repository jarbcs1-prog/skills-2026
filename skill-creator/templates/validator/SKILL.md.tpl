---
name: {{name}}
description: {{description}}
---

# {{name}}

{{description}}

## When to use

Trigger this skill when the user wants inputs, files or data checked against rules — validation, linting, conformance checks.

## Working

1. Define the validation rules (or load them from `references/`).
2. Run checks systematically; use `scripts/` for repeatable checks.
3. Record each violation with its location and the rule it violates.
4. Report a pass/fail summary, not just a list.

## Output

A validation report listing violations (with locations and rules) and a pass/fail summary.

## Verification

- [ ] Rules are explicitly defined
- [ ] Each violation includes location and rule
- [ ] Pass/fail summary is unambiguous
- [ ] False positives investigated
- [ ] `references/` consulted when relevant

## Resources

- `scripts/` — executable helpers for deterministic tasks
- `references/` — additional documentation loaded as needed
- `assets/` — files used in output
- `evals/evals.json` — test cases for this skill
