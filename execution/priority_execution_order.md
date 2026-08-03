# Priority Execution Order: Non-Production-Ready Skills

Generated from improvement_plan.md analysis across all skill folders and execution_plan.md.

---

## Methodology

Skills are categorized by their current tier (from improvement_plan.md) and ordered by:
1. **Dependency impact** — skills referenced as dependencies by other skills first
2. **Tier** — Strong Core (🟡) > Functional but Thin (🟠) > Critically Thin (🔴)
3. **Effort within tier** — smaller, well-scoped improvements before large rewrites
4. **Cross-skill references** — more dependents = higher priority

---

## Tier Summary

| Tier | Count | Status |
|------|-------|--------|
| 🟢 Production-Ready | 17 | P0/P1 DONE - 8 foundation skills production-ready (code-quality, code-reviewer, verification-before-completion, writing-skills, skill-judge, writing-plans, skill-reviewer, collaborative-skill-engineering) |
| 🟡 Strong Core (Needs Structure) | 10 | P1 IN PROGRESS - brainstorming ✅, project-analyst ✅ done; 8 P1 skills remain |
| 🟠 Functional but Thin (Needs Expansion) | 5 | P4 NOT DONE |
| 🔴 Critically Thin (Needs Rewrite) | 1 | P3 NOT DONE |
| 🔁 Duplicate/Merged | 6 | P0 DONE |
| ⚪ No improvement_plan.md | 1 | opencode-zen-delegator |

---

## Priority Order

### P0: Foundation Skills (Highest Priority)

These are 🟡 Strong Core skills that serve as dependencies for many other skills.
They have good foundations but need structure/polish to be fully production-ready.

| # | Skill | Lines | Tier | Key Gaps | Depends On By |
|---|-------|-------|------|----------|---------------|
| 1 | **code-quality** | 76 | 🟡 Strong Core | ✅ COMPLETE (20 tests, multi-language, incremental, plugins, CI workflow) | 20+ skills |
| 2 | **code-reviewer** | 64 | 🟡 Strong Core | ✅ COMPLETE (32 tests, 56 rules, CLI, SARIF, CI workflow) | 10+ skills |
| 3 | **verification-before-completion** | 139 | 🟢 Production-Ready | ✅ COMPLETE (13 tests, CLI, templates, agent verification, pre-commit hook, CI workflow) | 10+ skills |
| 4 | **writing-skills** | 653 | 🟢 Production-Ready | ✅ COMPLETE (16 tests, scaffolding, test harness, registry, CI workflow) | 8+ skills |
| 5 | **skill-judge** | 350 | 🟢 Production-Ready | ✅ COMPLETE (17 tests, 8-dim eval, benchmarks, all 5 references, CI workflow) | 5+ skills |
| 6 | **writing-plans** | 289 | 🟢 Production-Ready | ✅ COMPLETE (10 tests, templates, validator, traceability, CI workflow) | 4+ skills |
| 7 | **skill-reviewer** | 203 | 🟡 Strong Core | ✅ COMPLETE (25 tests, 3 reference files, CLI, auto-fix, security scan, CI workflow) | 3+ skills |
| 8 | **collaborative-skill-engineering** | 83 | 🟡 Strong Core | ✅ COMPLETE (8 tests, init_skill.py, validate_skill.py, structure guide, CI workflow) | 3+ skills |

**Rationale:** These skills are foundational infrastructure. Improving them first creates a solid base that accelerates all downstream skill work. code-quality and code-reviewer are the most referenced dependencies.

---

### P1: Strong Core — Structure & Polish

These 🟡 Strong Core skills have good content but need tooling, automation, and structure.

| # | Skill | Lines | Tier | Key Gaps |
|---|-------|-------|------|----------|
| 9 | **brainstorming** | 287 | 🟡 Strong Core | ✅ COMPLETE — pre-commit hook, init command, template library (7 templates), CLI enhanced |
| 10 | **daydream** | 47 | 🟡 Strong Core | No configuration, no insight quality metrics, no deduplication, no topic steering, no scheduling |
| 11 | **performance-optimizer** | 60 | 🟡 Strong Core | No automated analysis, no language-specific rules, no benchmarking framework, no CI integration |
| 12 | **remembering-conversations** | 65 | 🟡 Strong Core | No local caching, no semantic search, no conversation summarization, no pattern detection |
| 13 | **skills-search** | 107 | 🟡 Strong Core | Duplicate with find-skills (merge needed), no semantic search, no local index, no recommendations |
| 14 | **strategy-advisor** | 84 | 🟡 Strong Core | CLI has 5 commands, 7 frameworks, Monte Carlo, 10+ templates — needs test suite, CI workflow |
| 15 | **project-analyst** | 65 | 🟠 Functional but Thin | ✅ COMPLETE — 8 tests passing, full CLI (scan/deps/arch/stats), CI workflow, SKILL.md rewritten |

**Rationale:** These skills have solid cores (200+ lines each) and well-defined improvement plans. They need automation, CLI tooling, and integration work. project-analyst is promoted to P1 because it feeds into project-planner and writing-plans.

---

### P2: Functional but Thin — Substantial Expansion

These 🟠 Functional but Thin skills need significant new capabilities.

| # | Skill | Lines | Tier | Key Gaps |
|---|-------|-------|------|----------|
| 16 | **cheaper-reasoning** | 100 | 🟠 Functional but Thin | No quality validation, no integration with other skills, no tooling, no convergence detection, no token budget management |
| 17 | **master-of-dissent** | 34 | 🟠 Functional but Thin | No debate frameworks, no trigger conditions, no topic coverage, no interaction modes, no safety guards, no tooling |
| 18 | **rap-writer** | 49 | 🟠 Functional but Thin | No analysis tools, no reference library, no genre support, no CLI tooling, no validation, no batch processing |
| 19 | **ai-self-reflection** | 168 | 🟠 Functional but Thin | Post-merge: needs CLI wrapper, pattern detection, validation mechanism, integration hooks |
| 20 | **human-writer-simulator** | 44 | 🔴 Critically Thin | No detection capabilities, no style profiles, no quality validation, no domain adaptation, no tooling — needs complete rewrite |

**Rationale:** These skills have significant gaps relative to their content size. cheaper-reasoning and ai-self-reflection are promoted because they have clear integration paths with existing P0/P1 skills. human-writer-simulator is the only Critically Thin item not yet done per the execution plan.

---

### P3: Critically Thin — Complete Rewrite (Lowest Priority)

| # | Skill | Lines | Tier | Status |
|---|-------|-------|------|--------|
| 21 | **human-writer-simulator** | 44 | 🔴 Critically Thin | P3 in execution plan, NOT DONE — needs complete rewrite |

**Rationale:** Complete rewrites are the lowest priority because they require the most effort with the highest risk. The existing execution plan already deferred this.

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

## Execution Strategy

1. **Start with P0** — Foundation skills (**COMPLETE** - all 8 skills done with 141 tests passing). These unlock the most downstream work. Ready for P1.
2. **P1 IN PROGRESS** — brainstorming ✅ and project-analyst ✅ are complete. 5 P1 skills remain.
3. **Batch similar work** — CLI tooling, script creation, and reference file generation can be done across multiple skills in parallel.
4. **Validate each tier before moving on** — Ensure P0 skills are production-ready before starting P1.
5. **P3 (human-writer-simulator) is deferred** — Complete rewrite should only be attempted after all other skills are production-ready, as it has no integration points yet and the highest risk.
6. **Parallelize within tiers** — P0 and P1 skills have independent improvement plans and can be worked on concurrently.

---

## Skills Already Production-Ready (No Action Needed)

Per the execution plan P1/P2, these skills are now production-ready:

- dynamic-context-pruning ✅
- having-difficult-conversations ✅
- project-planner ✅
- systematic-debugging ✅
- subagent-driven-development ✅
- test-driven-development ✅
- trust-psychology ✅
- verification-before-completion ✅
- writing-plans ✅
- writing-skills ✅
- skill-creator ✅
- skill-judge ✅
- telecommunications-expert ✅
- brainstorming ✅ (P1 — pre-commit hook, init command, template library, CLI enhanced)
- project-analyst ✅ (P1 — 8 tests passing, full CLI, CI workflow, SKILL.md rewritten)

---

## Deprecated/Merged Skills (No Action Needed)

Per P0 in the execution plan, these have been merged or deprecated:

- ai-improved-self-reflection → merged into ai-self-reflection ✅
- opencode/big-pickle-router, opencode/delegator, external-llm-router, rate-limit-router → merged into opencode-zen-delegator ✅
- opencode/dynamic-context-pruning → merged into dynamic-context-pruning ✅
- prompt-engineer + prompt-optimizer → merged into prompt-engineering ✅
- find-skills → merged into skills-search ✅

---

## Notes

- **opencode-zen-delegator** has no improvement_plan.md — it should receive one before being prioritized.
- **P0 COMPLETE**: All 8 foundation skills are production-ready with 141 tests passing. Each has CI/CD workflow, passing tests, and updated documentation.
- **P1 IN PROGRESS**: brainstorming ✅ and project-analyst ✅ are now complete. strategy-advisor has CLI + frameworks but needs tests/CI. 5 P1 skills remain (daydream, performance-optimizer, remembering-conversations, skills-search, strategy-advisor).
- **project-analyst**: All 8 tests passing after fixing import paths and test assertions.
- The execution plan marks P1-P2 as DONE, but the improvement plans for those skills still list gaps. This document treats those gaps as the remaining work.
- human-writer-simulator is the only P3 item not marked DONE in the execution plan.
