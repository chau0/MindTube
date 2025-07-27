# AGENT_GUIDE — MindTube (P0)

**Version:** 2025-07-27 (JST)  
**Scope:** Rules and conventions for AI agent contributors

## 1) Guardrails
- Change only files listed in each ticket.
- Never leak secrets, API keys, or user data. Redact in logs.
- Respect YouTube ToS. Do **not** add scraping beyond approved transcript sources (see `docs/TRANSCRIPT_POLICY.md`).

## 2) Code quality
- Python 3.12; `ruff` + `black` + `mypy` (strict).
- Type hints required for public functions.
- Keep functions <50 LOC; modules <500 LOC. Prefer pure functions.

## 3) Testing
- `pytest` for unit/integration; golden fixtures for prompts and pipelines.
- New code must include tests. Minimum module coverage: 90% for pipeline utilities.

## 4) Performance & cost
- Token budgets are enforced; do not raise defaults without ticket approval.
- Use fast tier for map, HQ tier for reduce. See `docs/COST_POLICY.md`.

## 5) Observability
- Log JSON with `runId`, `stage`, `ms`, `error_code` (see `docs/OBSERVABILITY.md`).

## 6) Stop conditions
- If tests fail twice after changes → stop and post diagnostics.
- If encountering provider 429 storms → stop; label ticket with `needs-ops`.

## 7) Commit/PR
- Conventional commits; link ticket ID in title: `T-014: Implement chunker ...`
- Update relevant docs when contracts change.
