---
name: {{name}}
description: {{description}}
---

# {{name}}

{{description}}

## When to use

Trigger this skill when the user wants to connect to, call or synchronize with an external service, API or system.

## Working

1. Read the service documentation (or `references/`) to learn auth, endpoints and limits.
2. Configure credentials via environment variables — never hardcode secrets.
3. Implement the integration in `scripts/` with structured error handling.
4. Respect rate limits, timeouts and pagination.
5. Run a smoke test against the real or a stubbed endpoint.

## Output

A working integration with the external service, including auth, error handling, retries and a smoke test.

## Verification

- [ ] Auth flows are configured via environment variables
- [ ] Errors, rate limits and timeouts are handled
- [ ] A smoke test confirms connectivity
- [ ] No secrets appear in code or logs
- [ ] `references/` consulted when relevant

## Resources

- `scripts/` — executable helpers for deterministic tasks
- `references/` — additional documentation loaded as needed
- `assets/` — files used in output
- `evals/evals.json` — test cases for this skill
