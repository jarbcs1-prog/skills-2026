---
name: {{name}}
description: {{description}}
---

# {{name}}

{{description}}

## When to use

Trigger this skill when the user wants code, content or assets produced from a specification — generation, creation, drafting.

## Working

1. Derive a concrete specification from the request; ask if ambiguous.
2. Generate output consistent in style, structure and format.
3. Use `scripts/` for anything deterministic or repetitive.
4. Verify the output against the specification before delivering.

## Output

A generated artifact matching the specification, consistent in style, with verification.

## Verification

- [ ] Output matches the specification
- [ ] Style and structure are internally consistent
- [ ] Deterministic parts delegated to `scripts/`
- [ ] Output verified against expectations
- [ ] `references/` consulted when relevant

## Resources

- `scripts/` — executable helpers for deterministic tasks
- `references/` — additional documentation loaded as needed
- `assets/` — files used in output
- `evals/evals.json` — test cases for this skill
