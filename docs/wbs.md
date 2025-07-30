# YouTube Note Taker — Work Breakdown Structure (WBS)

> Paste this file into your repo as `docs/wbs.md`.

## Legend
- **Deps** = prerequisites by Task ID
- **Est.** = effort in focused hours (single experienced dev)
- **DoD** = Definition of Done (checklist)

---

## Phase 1 — CLI MVP (library‑first)

**Goal:** Given a YouTube URL, fetch transcript (with fallbacks), summarize via Gemini (map‑reduce), and write validated JSON artifacts under `data/<video_id>/`.

| ID | Task | What you’ll do | Deps | Est. | DoD |
|---|---|---|---|---:|---|
| **1.1** | Repo & tooling bootstrap | Init git, `uv`, `pyproject.toml`, `ruff`, `pyright`, `pytest`, `Makefile`. | — | 2 | `make setup/lint/test` succeed; CI runs lint+tests. |
| **1.2** | Config & secrets | Add `.env` loading (pydantic-settings), `.env.example`, Gemini key, proxy vars. | 1.1 | 1 | Config validated at startup; secrets not logged. |
| **1.3** | Scaffold modules | Create `ytnote/{cli,core,io,llm,models,qa}` + `data/` layout. | 1.1 | 1 | Packages import cleanly; type-check passes. |
| **1.4** | Video ID extractor | Robustly parse YouTube URLs/shorts; unit tests with fixtures. | 1.3 | 2 | Handles `watch`, `shorts`, `youtu.be`; tests green. |
| **1.5** | Transcript fetch (primary) | `youtube-transcript-api` fetch by preferred langs; errors mapped. | 1.4 | 3 | Saves `transcript.json` schema; retries/backoff; tests. |
| **1.6** | Transcript fallback | Optional `yt-dlp` auto-captions; feature‑flagged. | 1.5 | 2 | If primary fails and fallback enabled, produces transcript; tests. |
| **1.7** | Normalize transcript | Sentence/segment normalize: `{start,end,text,lang}`; merge tiny segments. | 1.5 | 2 | Deterministic output; golden file tests. |
| **1.8** | Token‑aware chunker | Split by ~1–2k tokens, respect sentence boundaries; token estimate util. | 1.7 | 3 | Same input ⇒ same chunks; unit & property tests. |
| **1.9** | Models & schemas | Pydantic models for `Summary`, `MainIdea`, `Takeaway`, `Artifacts`. | 1.3 | 2 | All artifacts validate; schema doc generated. |
| **1.10** | Gemini client wrapper | JSON‑only calls, retries, timeouts; invalid‑JSON repair loop. | 1.2,1.9 | 3 | 3 failure modes tested (timeout, 429, invalid JSON). |
| **1.11** | Map prompts | Per‑chunk “map” prompt → `{key_points[], summary}` JSON. | 1.8,1.10 | 2 | Mocked client tests; schema‑validated outputs. |
| **1.12** | Reduce prompt | Merge chunk maps → `{summary, main_ideas[], takeaways[]}`. | 1.11 | 2 | Stable merge; deterministic ordering; tests. |
| **1.13** | Caching & idempotency | Cache by `video_id`; `--force` to overwrite. | 1.5,1.12 | 1 | Re‑run without `--force` is a no‑op; logged “cache hit”. |
| **1.14** | CLI commands (Typer) | `fetch`, `summarize`, `ideas`, `takeaways`, `process`. | 1.13 | 2 | Commands work end‑to‑end; help text complete. |
| **1.15** | Structured logging | JSON logs with `video_id`, step, duration, token_used. | 1.14 | 1 | Sample logs captured; redaction verified. |
| **1.16** | Tests & coverage | Unit+integration; fixtures for 3 videos; ≥80% core/models. | 1.12,1.14 | 3 | Coverage report ≥80%; CI green. |
| **1.17** | Docs & examples | README quickstart; example commands; troubleshooting. | 1.16 | 1 | Fresh clone → user can process 1 video in <5 min. |
| **1.18** | Smoke run (3 vids) | Human validation: human captions, auto captions, no captions. | 1.16 | 1 | Artifacts present under `data/<video_id>/`; spot check OK. |

**Phase 1 subtotal:** **30–32 h**
**Milestone:** `ytnote process <url>` generates validated JSON artifacts reproducibly.

---

## Phase 2 — API Wrapper (FastAPI)

**Goal:** Non‑blocking ingest + polling; artifacts retrievable via REST with schemas shared from Phase 1.

| ID | Task | What you’ll do | Deps | Est. | DoD |
|---|---|---|---|---:|---|
| **2.1** | FastAPI skeleton | App factory, settings, logging middleware, `/healthz`. | 1.x | 2 | Uvicorn starts; health returns 200 with build info. |
| **2.2** | Pydantic I/O models | Reuse Phase 1 schemas for API responses. | 2.1,1.9 | 1 | OpenAPI shows accurate schemas. |
| **2.3** | Job registry | In‑memory status store (`queued/running/done/error`) with TTL. | 2.1 | 2 | Concurrency test with 5 jobs; no race conditions. |
| **2.4** | Ingest endpoint | `POST /ingest {url,lang?,force?}` → `job_id`; starts background task. | 2.3,1.14 | 3 | Returns `job_id`; background completes; errors recorded. |
| **2.5** | Status endpoint | `GET /status/{job_id}` with progress hints. | 2.4 | 1 | Polling demo shows state transitions. |
| **2.6** | Artifacts endpoints | `GET /videos/{video_id}/summary|ideas|takeaways|transcript|mindmap`. | 2.2,1.13 | 3 | 200 with validated JSON; 404 on missing. |
| **2.7** | Captions endpoint | `POST /captions {url,lang?}` → transcript JSON only. | 2.2,1.5 | 1 | Returns normalized transcript; integration test. |
| **2.8** | Error mapping | Consistent 4xx/5xx schema; retry‑after headers for 429. | 2.4 | 1 | Postman tests pass; contract documented. |
| **2.9** | Rate limiting guard | Simple token bucket per IP. | 2.1 | 2 | Soak test confirms no overload; friendly 429. |
| **2.10** | OpenAPI & examples | Examples for each route; Postman/Bruno collection. | 2.6 | 1 | Collection exported; README API section updated. |
| **2.11** | Containerization | Dockerfile, `make api-up`, live reload dev compose. | 2.1 | 2 | `docker compose up` runs locally; health 200. |
| **2.12** | Tests | Unit (handlers) + integration (bg jobs); happy & sad paths. | 2.6 | 3 | CI green; 80% lines in `api/` & handlers. |

**Phase 2 subtotal:** **21–22 h**
**Milestone:** Non‑blocking ingest + polling; artifacts retrievable via REST.

---

## Phase 3 — Minimal UI

**Goal:** Simple page accepts URL, shows progress, renders results, and allows transcript download.

| ID | Task | What you’ll do | Deps | Est. | DoD |
|---|---|---|---|---:|---|
| **3.1** | UI scaffold | Minimal SPA (React/Vite) or static + HTMX; env config for API base. | 2.x | 3 | App builds; lint OK; `.env.example` present. |
| **3.2** | URL input form | URL + lang; client validation; call `/ingest`. | 3.1,2.4 | 2 | Invalid input blocked; valid shows “processing…”. |
| **3.3** | Status polling | Poll `/status/{job_id}`; progress UI; error states. | 3.2,2.5 | 2 | Visible progress; retry/backoff on network errors. |
| **3.4** | Results view | Fetch & render summary, ideas, takeaways. | 3.3,2.6 | 2 | Components render JSON deterministically. |
| **3.5** | Mind map viewer (opt) | Render Markmap/Mermaid or Cytoscape from JSON if present. | 3.4 | 2 | Mind map displays for sample video; togglable. |
| **3.6** | Download caption | Button to download transcript file. | 3.4,2.6 | 1 | Click downloads `.json`/`.vtt` as available. |
| **3.7** | UX polish | Empty/loading/error states; basic responsive layout. | 3.4 | 2 | Lighthouse perf ≥80; a11y basic checks pass. |
| **3.8** | E2E test | Playwright happy path (URL → results). | 3.4 | 2 | Headless run green in CI. |
| **3.9** | Deploy docs | README for UI dev & API config; `make ui-up`. | 3.1 | 1 | New dev can run UI in <5 min. |

**Phase 3 subtotal:** **16–17 h**
**Milestone:** One‑page UI from URL to results with visible progress and downloads.

---

## Optional / “Nice to Have”

| ID | Task | What you’ll do | Deps | Est. | DoD |
|---|---|---|---|---:|---|
| **4.1** | Mind map generation (backend) | LLM → graph JSON + Markmap Markdown. | 1.12 | 3 | Valid graph with ≤25 nodes; renders in UI. |
| **4.2** | Blog article generator | LLM turns `main_ideas` into outline + article JSON. | 1.12 | 3 | JSON schema for sections; sample export `.md`. |
| **4.3** | Simple QA over chunks | BM25 or embeddings; answers cite `chunk_ids`. | 1.8 | 5 | `POST /qa` returns answer+citations; accuracy spot‑check. |
| **4.4** | SQLite index | Track processed videos (title, duration, langs). | 2.6 | 2 | `/videos` list endpoint; migration script. |

**Optional subtotal:** **13–14 h**

---

## Roll‑up Estimates

- **Phase 1:** 30–32 h
- **Phase 2:** 21–22 h
- **Phase 3:** 16–17 h
- **Optional:** 13–14 h

**Core (P1–P3) total:** **67–71 hours**
Add **~15% buffer** for unknowns ⇒ **77–82 hours**.

---

## Critical Path
1. 1.5 → 1.7 → 1.8 → 1.10 → 1.11 → 1.12 → 1.14
2. 2.4 (ingest) → 2.5 (status) → 2.6 (artifacts)
3. 3.2 (submit) → 3.3 (poll) → 3.4 (render)

---

## Acceptance / Phase Milestones

- **P1 Acceptance:** Given a URL, `ytnote process` writes `transcript.json`, `chunks.jsonl`, `summary.json`, `main_ideas.json`, `takeaways.json` under `data/<video_id>/`. Re‑run without `--force` is a no‑op.
- **P2 Acceptance:** `POST /ingest` returns `job_id`; `GET /status` transitions to `done`; `GET /videos/{id}/summary` returns validated JSON.
- **P3 Acceptance:** UI accepts URL, shows progress, and renders results; transcript downloadable.

---

## Assumptions
- Gemini API access and quotas available.
- Workstation has Python 3.11+, `uv`; `yt-dlp` available if fallback enabled.
- Single developer; no heavy auth/hosting work in this sprint.
