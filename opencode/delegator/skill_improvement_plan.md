# opencode/delegator — Improvement Plan

## Assessment
Good — clean SKILL.md with OpenCode-specific naming. But missing scripts, ambiguous API key guidance, no README.

## Issues
1. **CRITICAL** — big_pickle_agent.py referenced in SKILL.md does not exist
2. **High** — Ambiguous "API key must be added to the script" language
3. **Medium** — No verify_new_key.py or test files
4. **Medium** — No README.md
5. **Low** — No .env.example
6. **Low** — No scripts/ directory

## Changes
1. Create scripts/big_pickle_agent.py
2. Create scripts/delegate_manager.py (or symlink)
3. Replace ambiguous API key language with explicit env var guidance
4. Add README.md
5. Add .env.example
6. Add verify_new_key.py
7. Add 1+ test file

## Verification
- All SKILL.md script paths resolve
- No ambiguous API key guidance remains
- uv run python -m py_compile passes
