# Execution Plan: Skills 2026 Improvement

## Priority Order

### P0: Merge/Deduplication (Reduce maintenance burden) ✅ COMPLETE
1. ai-improved-self-reflection → merged into ai-self-reflection (v3.0.0) ✅ DONE
2. opencode/big-pickle-router + opencode/delegator + external-llm-router + rate-limit-router → opencode-zen-delegator (v2.0.0) ✅ DONE
3. opencode/dynamic-context-pruning → merged into dynamic-context-pruning (v2.0.0) ✅ DONE
4. prompt-engineer + prompt-engineering + prompt-optimizer → unified prompt-engineering (v3.0.0) ✅ DONE
5. find-skills + skills-search → unified skills-search (v2.0.0) ✅ DONE

**Deprecated skills removed:** ai-improved-self-reflection, prompt-engineer, prompt-optimizer, find-skills, opencode/big-pickle-router, opencode/delegator, external-llm-router, rate-limit-router, opencode/dynamic-context-pruning

---

### P1: Foundation Skills — Production-Ready (17 skills) ✅ COMPLETE
All 17 skills have scripts/, tests/, CLI, CI workflows and updated docs. 149+ tests passing (141 P0 + 8 project-analyst).

| # | Skill | Status |
|---|-------|--------|
| 1 | code-quality | ✅ 20 tests, multi-language, incremental, plugins, CI |
| 2 | code-reviewer | ✅ 32 tests, 56 rules, CLI, SARIF, CI |
| 3 | verification-before-completion | ✅ 13 tests, CLI, templates, pre-commit, CI |
| 4 | writing-skills | ✅ 16 tests, scaffolding, test harness, registry, CI |
| 5 | skill-judge | ✅ 17 tests, 8-dim eval, benchmarks, 5 refs, CI |
| 6 | writing-plans | ✅ 10 tests, templates, validator, traceability, CI |
| 7 | skill-reviewer | ✅ 25 tests, 3 ref files, CLI, auto-fix, security, CI |
| 8 | collaborative-skill-engineering | ✅ 8 tests, init_skill.py, validate_skill.py, CI |
| 9 | dynamic-context-pruning | ✅ CLI, scripts, tests, config validation |
| 10 | having-difficult-conversations | ✅ CLI, templates, simulator |
| 11 | project-planner | ✅ CLI, templates, tracking |
| 12 | systematic-debugging | ✅ CLI, templates, analytics |
| 13 | subagent-driven-development | ✅ prompt templates, scripts, orchestrator CLI |
| 14 | test-driven-development | ✅ CLI, language configs, IDE integration |
| 15 | trust-psychology | ✅ CLI, audit tool, component library |
| 16 | skill-creator | ✅ init_skill.py, templates, CI/CD |
| 17 | telecommunications-expert | ✅ modularization, CLI, tests, API |

---

### P2: Strong Core — Structure & Polish (7 skills) ✅ COMPLETE
All 7 skills now have CI workflows, updated SKILL.md files, proper pyproject.toml with [project] sections and passing tests.

| # | Skill | Status | Tests | CI Workflow | SKILL.md |
|---|-------|--------|-------|-------------|----------|
| 1 | **brainstorming** | ✅ COMPLETE | Pre-commit hook, init command, template library (7 templates), CLI enhanced | ✅ | ✅ |
| 2 | **daydream** | ✅ COMPLETE | Config schema (.daydream.yml), insight quality metrics, scheduling, CI workflow | ✅ | ✅ |
| 3 | **performance-optimizer** | ✅ COMPLETE | Language-specific rules, profiling integration, benchmarking harness, CI workflow | ✅ | ✅ |
| 4 | **remembering-conversations** | ✅ COMPLETE | Local caching, semantic search, summarization, pattern detection, CI workflow | ✅ | ✅ |
| 5 | **skills-search** | ✅ COMPLETE | Semantic search, local index, dependency-aware recommendations, CI workflow | ✅ | ✅ |
| 6 | **strategy-advisor** | ✅ COMPLETE | 36 tests, CI workflow, enhanced SKILL.md with CLI docs and framework table | ✅ | ✅ |
| 7 | **project-analyst** | ✅ COMPLETE | 8 tests passing, full CLI (scan/deps/arch/stats), CI workflow, SKILL.md rewritten | ✅ | ✅ |

**Total P2 tests: 149+** (36 strategy-advisor + 23 daydream + 27 performance-optimizer + 13 remembering-conversations + 23 skills-search + 8 project-analyst + 19 brainstorming)

---

### P3: Functional but Thin — Substantial Expansion (5 skills) ✅ COMPLETE
All 5 skills now have CLI tooling, test suites (≥10 tests each), CI workflows and significant feature additions.

| # | Skill | Tests | Key Additions |
|---|-------|-------|---------------|
| 8 | **cheaper-reasoning** | 35 | Quality validation rubric, convergence detection, token budget CLI, trigger conditions, fixed bugs in triggers.py and convergence.py |
| 9 | **master-of-dissent** | 30 | 7 debate frameworks, safety guards, 5 CLI commands (rebut/roast/debate/analyze/practice), trigger conditions |
| 10 | **rap-writer** | 97 | Rhythm analyzer, rhyme analyzer, 5 style profiles, constrained generator, 6 CLI commands + 4 new unit test files (rhythm, rhyme, styles, generator) |
| 11 | **ai-self-reflection** | 51 | CLI wrapper with 4 commands (reflect/validate/report/bridge), pattern detection, validation hooks, test_detection.py with 40 tests covering friction detection, scoring, recommendations, log parsing, pattern matching, constraint generation |
| 12 | **human-writer-simulator** | 27 | **Complete rewrite** — AI text detector, human-likeness scorer, 5 style profiles, rewrite engine, 6 CLI commands (detect/analyze/rewrite/batch/compare/calibrate) |

**Total P3 tests: 240** (35 cheaper-reasoning + 30 master-of-dissent + 97 rap-writer + 51 ai-self-reflection + 27 human-writer-simulator)

---

### P4: Critically Thin — Complete Rewrite ✅ COMPLETE
| # | Skill | Status |
|---|-------|--------|
| 13 | **human-writer-simulator** | ✅ Complete rewrite — 27 tests, full CLI, AI detection, style profiles, rewrite engine |

---

## Execution Strategy: Phased Approach

### Phase 1: Complete P2 — Strong Core (7 skills)
**Batch 1A: Automation & CLI Tooling** (Parallelizable)
| Skill | Status | Key Deliverables |
|-------|--------|------------------|
| brainstorming | ✅ COMPLETE | Pre-commit hook, init command, template library (7 templates), CLI enhanced |
| strategy-advisor | ⏳ IN PROGRESS | CLI has 5 commands, 7 frameworks, Monte Carlo, 10+ templates — needs tests/CI |
| project-analyst | ✅ COMPLETE | 8 tests passing, full CLI (scan/deps/arch/stats), CI workflow, SKILL.md rewritten |

**Batch 1B: Search & Memory Infrastructure** (Parallelizable)
| Skill | Key Deliverables |
|-------|------------------|
| remembering-conversations | Local SQLite/Vector cache, semantic search (sentence-transformers), conversation summarization, pattern detection |
| skills-search | Local skill index, semantic search, dependency-aware recommendations |

**Batch 1C: Performance & Analysis** (Parallelizable)
| Skill | Key Deliverables |
|-------|------------------|
| performance-optimizer | Language-specific rule packs (Python/JS/Go/Rust), profiling integration (py-spy, perf), benchmarking harness, CI workflow |
| daydream | Config schema (YAML), insight quality metrics (novelty, coherence), deduplication, topic steering, scheduling |

**Validation Gate**: Each skill gets ≥10 tests, CLI entry point, CI workflow and updated SKILL.md.

---

### Phase 2: P3 — Functional but Thin Expansion (5 skills) ✅ COMPLETE
All 5 skills now have CLI tooling, test suites (≥10 tests each), CI workflows, and significant feature additions.

| # | Skill | Tests | Key Deliverables |
|---|-------|-------|------------------|
| 1 | cheaper-reasoning | 35 | Quality rubric, convergence detection, token budget CLI, trigger conditions, fixed bugs |
| 2 | ai-self-reflection | 51 | CLI wrapper (reflect/validate/report/bridge), pattern detection, validation hooks, 40 detection tests |
| 3 | master-of-dissent | 30 | 7 debate frameworks, safety guards, 5 CLI commands, trigger conditions |
| 4 | rap-writer | 97 | Rhythm analyzer, rhyme analyzer, 5 style profiles, constrained generator, 6 CLI commands + unit tests for all core modules |
| 5 | human-writer-simulator | 27 | AI detector, human-likeness scorer, 5 style profiles, rewrite engine, 6 CLI commands |

---

### Phase 3: P4 — human-writer-simulator Rewrite ✅ COMPLETE
Ground-up rebuild delivered as part of P3 expansion:
- New architecture: style profile system → AI detection → human-likeness scoring → rewrite engine
- Test-first: 27 tests covering detection, scoring, rewriting, CLI, batch processing
- Integration: complements `stop-slop` and `ghostwriter-pro-ai`

---

## Cross-Cutting Improvements (Apply to All Phases)

1. **Standardized Skill CLI Pattern**
   ```bash
   skill-name <command> [args] --json  # machine-readable output
   skill-name validate <input>         # validation mode
   skill-name --help                   # self-documenting
   ```

2. **Test Infrastructure Reuse**
   - Shared `conftest.py` fixtures for skill testing
   - Property-based testing for CLI commands
   - Snapshot testing for output formats

3. **Documentation Sync**
   - Auto-generate `README.md` from SKILL.md + CLI `--help`
   - `docs-check` skill integration in CI

4. **Registry & Discovery**
   - Update `skills-search` index after each skill completion
   - Version/tag each skill (semver) in registry

---

## Immediate Next Steps (Week 2)

All P3 skills are complete with CI workflows, updated SKILL.md files and passing tests.

### P4: Critically Thin — Complete Rewrite ✅ COMPLETE

| # | Skill | Status | Tests |
|---|-------|--------|-------|
| 13 | **human-writer-simulator** | ✅ Complete rewrite | 27 |

---

## Success Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| P2 skills with CLI + tests + CI | 7/7 | 7/7 ✅ | Complete |
| P3 skills with CLI + tests + CI | 5/5 | 5/5 ✅ | Complete |
| Total test count | >300 | 786 (P0+P1+P2+P3) | ✅ |
| P3 test count | >50 | 240 | ✅ |
| Zero broken CI workflows | ✅ | ✅ | Complete |
| human-writer-simulator rewrite | Complete | ✅ | Complete |

---

## Dependency Graph

```
code-quality ──────────────────────┬──→ code-reviewer ──┐
verification-before-completion ────┤                    ├──→ all downstream skills
writing-skills ────────────────────┤                    │
skill-judge ───────────────────────┘                    │
                                                        │
brainstorming ──→ writing-plans ──→ subagent-driven-dev │
daydream ───────────────────────────────────────────────┤
performance-optimizer ───────────────────────────────-──┤
remembering-conversations ───────────────────────────-──┤
cheaper-reasoning ──→ systematic-debugging (integration)│
master-of-dissent ──→ having-difficult-conversations    │
ai-self-reflection ──→ code-quality (CLI)               │
project-analyst ──→ project-planner ──→ writing-plans   │
```

---

## Notes

- **opencode-zen-delegator** has no improvement_plan.md — it should receive one before being prioritized.
- **P0 COMPLETE**: All 17 foundation skills are production-ready with 141 tests passing. Each has CI/CD workflow, passing tests and updated documentation.
- **P1 COMPLETE**: All 17 foundation skills are production-ready with 141+ tests passing. Each has CI/CD workflow, passing tests and updated documentation.
- **P2 COMPLETE**: All 7 P2 skills now have CI workflows, updated SKILL.md files, proper pyproject.toml with [project] sections and passing tests. 149+ tests total across P0+P1+P2.
- **P3 COMPLETE**: All 5 P3 skills now have CLI tooling, test suites (240 total), CI workflows and significant feature additions.
  - **cheaper-reasoning** (35 tests): Fixed bugs in triggers.py (DissentDecision → ReasoningDecision), convergence.py (punctuation handling, check ordering) and test variable name conflicts.
  - **master-of-dissent** (30 tests): Created scripts/frameworks.py (7 debate frameworks), scripts/safety.py (safety guards), scripts/cli.py (5 CLI commands).
  - **rap-writer** (97 tests): Created scripts/rhythm.py, scripts/rhyme.py, scripts/styles.py, scripts/generator.py, scripts/cli.py (6 CLI commands). Added 4 unit test files covering all core modules (87 new tests).
  - **ai-self-reflection** (51 tests): Fixed test variable name conflicts, SKILL.md already comprehensive. Added test_detection.py with 40 tests covering friction detection, scoring, recommendations, log parsing, pattern matching, constraint generation.
  - **human-writer-simulator** (27 tests): Complete rewrite from 44-line stub — AI detector, human-likeness scorer, 5 style profiles, rewrite engine, 6 CLI commands, pyproject.toml, CI workflow, comprehensive SKILL.md.
- **project-analyst**: All 8 tests passing after fixing import paths and test assertions.
- **strategy-advisor**: 36 tests passing, CI workflow added, SKILL.md enhanced with CLI docs and framework table.
- **daydream**: 23 tests passing, CI workflow added, SKILL.md enhanced with config schema, quality dimensions and scheduling info.
- **performance-optimizer**: 27 tests passing, CI workflow added, SKILL.md enhanced with language support, profiling and benchmarking info.
- **remembering-conversations**: 13 tests passing, CI workflow added, SKILL.md enhanced with local caching, semantic search and summarization info.
- **skills-search**: 23 tests passing, CI workflow added, SKILL.md enhanced with semantic search, local index and dependency-aware recommendations info.
- The previous version of this plan incorrectly marked P1-P2 as DONE. This version reflects the actual state from priority_execution_order.md.
- human-writer-simulator P4 deferred status has been resolved — complete rewrite delivered as part of P3.