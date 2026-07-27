# Rate Limit Router — Improvement Plan

## Completed

- [x] Move script from root to `scripts/` directory (P0)
- [x] Fix config key mismatch: JSON uses `opencode-zen` but code accesses `zen` (P0)
- [x] Remove hardcoded API keys from config.json — use env vars instead (P0)
- [x] Add `get_api_key()` function reading from `ZEN_API_KEY`/`OPENROUTER_API_KEY` env vars (P0)
- [x] Fix duplicate keys in `reverse_map` (P0)
- [x] Create `scripts/__init__.py` (P1)
- [x] Create `.env.example` (P1)
- [x] Update SKILL.md with correct paths and env var docs (P1)
- [x] Fix test file: remove hardcoded keys, mock `get_api_key`, fix assertions (P1)
- [x] Create `README.md` (P2)

## Remaining

- [ ] Add streaming SSE test (currently only non-stream tested) — P3
- [ ] Add `requests` dependency to a requirements.txt — P3
