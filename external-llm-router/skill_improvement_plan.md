# Skill Improvement Plan — external-llm-router

**Date:** 2026-07-26
**Status:** Draft
**Overall Completeness:** 25%

---

## Current State Assessment

### What Exists
- `SKILL.md` — 43 lines, minimal but structurally sound (3 workflows: configure/monitor/delegate)
- `references/api_reference.md` — 20 lines, lists OpenCode Zen/OpenAI/Anthropic endpoints and models

### What's Missing
| Gap | Severity | Effort |
|-----|----------|--------|
| `scripts/` is EMPTY — SKILL.md references `agent.py` and `monitor.py` that don't exist | **CRITICAL** | 4–5h |
| `templates/` is EMPTY | Medium | 1h |
| No error handling documentation | Medium | 1h |
| No rate-limit retry logic documented | Medium | 1h |
| No `.env.example` for API keys | High | 15min |
| No tests | Medium | 2h |
| No README.md | Low | 30min |
| SKILL.md line 31 references `$API_KEY $URL $MODEL` positional args — fragile | Medium | 30min |
| No multi-provider failover logic | Low | 2h |
| `opencode/big-pickle` model name may need update | Low | 10min |

---

## Priority Changes

### Phase 1: Core Functionality (Must-Have)

#### 1.1 Create `scripts/agent.py` — Multi-provider LLM client
**Priority:** P0
**Effort:** 2–3h
**Depends on:** None

SKILL.md references this as "a generic client for OpenAI and Anthropic-compatible endpoints." Must implement:
- `agent.py <api_key> <url> <model> <prompt> [context_file]` CLI interface
- Support OpenAI-compatible (chat/completions) and Anthropic (messages) endpoints
- Parse `reasoning_content` from response (per Best Practices, line 41)
- Load/save `context.json` for stateful handoff
- Proper error handling (429, 500, timeout)

#### 1.2 Create `scripts/monitor.py` — Token usage tracker
**Priority:** P0
**Effort:** 1–2h
**Depends on:** None

SKILL.md references: `python3 scripts/monitor.py daily_usage.json <tokens_used> <limit>`. Must implement:
- JSON-based cumulative token tracking
- Daily reset capability
- Return exit code 1 when limit exceeded
- Support `--reset` flag for daily reset

#### 1.3 Create `.env.example`
**Priority:** P0
**Effort:** 15min
**Depends on:** None

```
OPENCODE_API_KEY=your-opencode-zen-key
OPENROUTER_API_KEY=your-openrouter-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### Phase 2: Quality & Robustness

#### 2.1 Add retry logic with exponential backoff
**Priority:** P1
**Effort:** 1h
**Depends on:** 1.1

Handle 429 (rate limit) and 5xx errors with configurable retry. Document in SKILL.md.

#### 2.2 Add `.env` loading to agent.py
**Priority:** P1
**Effort:** 30min
**Depends on:** 1.1

Use `python-dotenv` or `os.environ` to load keys from `.env` instead of requiring CLI args.

#### 2.3 Add tests
**Priority:** P1
**Effort:** 2h
**Depends on:** 1.1, 1.2

Create `tests/test_agent.py` and `tests/test_monitor.py`:
- Test provider URL routing (OpenAI vs Anthropic format)
- Test context.json load/save round-trip
- Test monitor daily accumulation and limit check
- Mock HTTP responses

#### 2.4 Add templates
**Priority:** P2
**Effort:** 1h
**Depends on:** None

Create:
- `templates/context.json.template` — Starter context file structure
- `templates/config.template.json` — Provider configuration template

### Phase 3: Polish

#### 3.1 Add README.md
**Priority:** P2
**Effort:** 30min
**Depends on:** 1.1, 1.2

Quick start, provider setup, usage examples.

#### 3.2 Add multi-provider failover
**Priority:** P3
**Effort:** 2h
**Depends on:** 1.1

Chain providers: try OpenCode Zen → fallback to OpenRouter → fallback to direct Anthropic.

#### 3.3 Update SKILL.md with complete documentation
**Priority:** P2
**Effort:** 1h
**Depends on:** 1.1, 1.2

Add:
- Error handling section
- Retry behavior documentation
- Environment variable reference
- Updated CLI examples with actual output

---

## Dependency Graph

```
1.1 (agent.py) ──→ 2.1 (retry) ──→ 3.2 (failover)
              ──→ 2.2 (.env loading) ──→ 3.3 (SKILL.md update)
              ──→ 2.3 (tests)
              ──→ 3.1 (README)
1.2 (monitor.py) ──→ 2.3 (tests)
              ──→ 3.1 (README)
1.3 (.env.example) ──→ (independent)
2.4 (templates) ──→ (independent)
```

## Acceptance Criteria

- [ ] `python scripts/agent.py` runs without import errors
- [ ] `python scripts/monitor.py` runs and tracks usage
- [ ] `pytest tests/` passes with 0 errors
- [ ] `.env.example` exists with all provider keys documented
- [ ] SKILL.md scripts section matches actual files in `scripts/`
- [ ] README.md exists with install + usage
- [ ] No placeholder files in scripts/ or templates/
