---
name: {{name}}
description: {{description}}
---

# {{name}}

{{description}}

## When to use

Trigger this skill when the user wants data converted between formats, schemas or structures — conversion, mapping, migration of data.

## Working

1. Define source and target schemas precisely.
2. Map every field; document mappings in `scripts/` or `references/`.
3. Handle missing, null and malformed values explicitly — do not silently drop data.
4. Verify row/record counts and spot-check samples after conversion.

## Output

A transformed dataset in the target schema, with field mapping and a verification report.

## Verification

- [ ] Field mapping is explicit and complete
- [ ] No records silently dropped or altered
- [ ] Counts verified before and after
- [ ] Spot checks pass
- [ ] `references/` consulted when relevant

## Resources

- `scripts/` — executable helpers for deterministic tasks
- `references/` — additional documentation loaded as needed
- `assets/` — files used in output
- `evals/evals.json` — test cases for this skill
