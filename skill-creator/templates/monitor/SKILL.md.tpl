---
name: {{name}}
description: {{description}}
---

# {{name}}

{{description}}

## When to use

Trigger this skill when the user wants systems or data watched for problems — monitoring, alerts, observability, dashboards of health.

## Working

1. Define the metrics, thresholds and alert recipients.
2. Sample on schedule; record observations in `scripts/`.
3. Compare each observation against thresholds (`warning`, `critical`).
4. Alert immediately on breach, with context and severity.
5. Confirm recovery once the metric returns to normal.

## Output

An observation log plus alerts when metrics breach thresholds, each with severity and context.

## Verification

- [ ] Metrics and thresholds are explicitly defined
- [ ] Sampling is on schedule and logged
- [ ] Alerts include severity and context
- [ ] Recovery is confirmed after breaches
- [ ] `references/` consulted when relevant

## Resources

- `scripts/` — executable helpers for deterministic tasks
- `references/` — additional documentation loaded as needed
- `assets/` — files used in output
- `evals/evals.json` — test cases for this skill
