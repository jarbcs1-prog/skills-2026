# opencode/big-pickle-router — Improvement Plan

## Assessment
Poor — no SKILL.md, hardcoded API key, wrong model name, wrong endpoint, inconsistent limits, Linux paths.

## Issues
1. **CRITICAL** — Hardcoded API key
2. **High** — Wrong model name: "big-pickle" should be "opencode/big-pickle"
3. **High** — Wrong endpoint in verify_new_key.py
4. **Medium** — No SKILL.md
5. **Medium** — Inconsistent token limits (1,300 vs 200,000)
6. **Medium** — Inconsistent endpoints across test files
7. **Low** — /home/ubuntu/ paths in README
8. **Low** — No test files
9. **Low** — No scripts/ or __init__.py
10. **Low** — No .env.example

## Changes
1. Remove hardcoded API key
2. Create SKILL.md
3. Fix model name and endpoint
4. Unify token limit docs
5. Standardize paths
6. Add __init__.py
7. Add .env.example and README.md
8. Add 2+ test files

## Verification
- Grep for hardcoded keys returns zero matches
- All SKILL.md paths resolve
- uv run python -m py_compile passes
