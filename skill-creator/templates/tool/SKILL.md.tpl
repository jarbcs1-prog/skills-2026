---
name: {{name}}
description: {{description}}
---

# {{name}}

{{description}}

## When to use

Trigger this skill when the user's intent matches the description above. Match on intent and context (file types, conversion, manipulation), not exact wording.

## Working

1. Identify the input file format and target format.
2. Inspect the input to understand its structure before modifying it.
3. Use bundled scripts in `scripts/` for deterministic operations (create, edit, convert).
4. Preserve existing content, formatting and metadata when editing.
5. If a file format is unsupported, say so clearly and suggest an alternative.

## Output

A valid file in the target format, verified to open correctly and match the expected content.

## Verification

- [ ] Output file exists and opens correctly
- [ ] Content and formatting match the documented expectations
- [ ] Edge cases (empty input, malformed files) handled gracefully
- [ ] Deterministic work delegated to `scripts/`
- [ ] `references/` consulted when relevant

## Resources

- `scripts/` — executable helpers for deterministic tasks
- `references/` — additional documentation loaded as needed
- `assets/` — files used in output
- `evals/evals.json` — test cases for this skill
