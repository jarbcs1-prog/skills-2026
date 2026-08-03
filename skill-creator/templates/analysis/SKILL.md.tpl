---
name: {{name}}
description: {{description}}
---

# {{name}}

{{description}}

## When to use

Trigger this skill when the user wants to understand, quantify or report on data — analysis, exploration, dashboards, statistics, findings.

## Working

1. Confirm the data source and the question being answered.
2. Load and clean the data; check for missing or malformed values.
3. Perform the analysis with reproducible steps (scripts in `scripts/`).
4. Validate results against known values or sanity checks.
5. Summarize findings with concrete numbers and caveats.

## Output

A structured report (or dataset) containing the analysis, key findings, methodology and any caveats.

## Verification

- [ ] Data quality issues were identified and documented
- [ ] Analysis steps are reproducible from `scripts/`
- [ ] Findings are backed by concrete numbers
- [ ] Edge cases (missing data, empty sets) handled gracefully
- [ ] `references/` consulted when relevant

## Resources

- `scripts/` — executable helpers for deterministic tasks
- `references/` — additional documentation loaded as needed
- `assets/` — files used in output
- `evals/evals.json` — test cases for this skill
