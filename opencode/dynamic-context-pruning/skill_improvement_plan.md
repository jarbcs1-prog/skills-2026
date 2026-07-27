# opencode/dynamic-context-pruning — Improvement Plan

## Assessment
Excellent content but incomplete bundling — SKILL.md has timestamp-based compaction, AST-aware pruning, tiered reduction. But scripts, references and examples are missing.

## Issues
1. **High** — Scripts referenced in SKILL.md do not exist (context_monitor.py, compaction.py, summarization.py, file_offloader.py, kv_cache.py)
2. **High** — Reference files do not exist (compaction_strategies.md, summarization_schemas.md, etc.) — only opencode_context_engineering.md exists
3. **High** — Examples referenced do not exist (basic_opencode_loop.py, full_opencode_loop.py)
4. **Medium** — Config has undocumented fields (ast, file_pool, adaptive, locked_tool_defs)
5. **Medium** — No test files
6. **Low** — No scripts/__init__.py
7. **Low** — No README.md
8. **Low** — Version history too detailed

## Changes
1. Copy missing scripts from .agents/skills/opencode-context-pruning/scripts/
2. Copy missing reference files
3. Create examples/ directory with loop files
4. Document undocumented config fields
5. Add test files
6. Add __init__.py
7. Add README.md
8. Trim version history

## Verification
- All SKILL.md script references resolve
- All reference paths resolve
- All example paths resolve
- uv run python -m py_compile passes
