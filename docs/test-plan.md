# MindTube — MVP Test Plan

**File:** /docs/test-plan.md  
**Version:** v0.1 (2025‑07‑26, JST)  
**Owner:** You (PM/Builder)

---

## 0) Purpose & Scope

This plan defines how we validate the MindTube MVP:
- Input: **YouTube URL**
- Output: **Summary / Key Ideas / Takeaways / Transcript** with optional timestamps and **Markdown export**.
- Platforms: Desktop web (Chrome, Edge, Safari, Firefox latest), responsive but mobile polish is **non‑goal** for MVP.

**Out of Scope (MVP):** Mind map rendering, Notion/PDF export, multi‑user accounts, batch jobs, full i18n beyond EN/JA.

---

## 1) Test Strategy

We’ll combine **automated** (unit/integration/API) and **manual** (golden set rubric) tests:
- **Unit**: chunking, timestamp conversions, Markdown generator, caching, validators.
- **Integration**: carmalize; map/reduce pipeline using mocked LLM.
- **API/E2E**: `/ingest` → `/status` → `/result` with real captions for short public videos.
- **Manual QA**: Human rubric on 1ption fetch → no0–15 diverse videos; accessibility pass.
- **Non‑functional**: performance (latency), cost guardrails, reliability (success rate).

Exit when MVP acceptance metrics are met (see §9).

---

## 2) Test Environments

- **Local Dev:** Next.js + FastAPI; optional SQLite. Artifacts in `./data/artifacts`.
- **Staging (Small VPS/Render):** Postgres + file storage (disk or S3‑compatible).

**Browsers:** Chrome (latest), Edge (latest), Safari 17+, Firefox (latest).  
**Network:** Test on fast (>50Mbps) and constrained (Fast 3G throttling) profiles.

---

## 3) Test Data (Golden Set & Fixtures)

Create a **Golden Set** of 10–15 videos (store IDs in `/tests/golden_set.json`):
- **Durations**: 5–10min (x5), 20–40min (x4), ~90min (x2).
- **Categories**: lecture, interview, explainer, tutorial.
- **Captions**: with captions (x8+), **no captions** (x2) → triggers ASR flow (if enabled).
- **Languages**: EN (x6), JA (x3). If non‑EN/JA appear, mark as “best‑effort”.
- **Edge cases**: music/no speech (x1), live stream VOD (x1), heavy accent (x1), unlisted (x1).

> **Note:** Do not store actual media. Keep only `video_id`, `title`, `channel`, and metadata.

**Synthetic Fixtures** (avoid model cost in tests):
- `fixtures/transcript_short.json` — 8–10 segments, 12:00 total.
- `fixtures/transcript_long.json` — 60:00 total.
- `fixtures/no_captions.json` — empty → ASR prompt.
- `fixtures/private_or_deleted.json` — simulate 403/404.

---

## 4) KPIs, SLAs & Measurements

| KPI | Target (MVP) | How to Measure |
|---|---|---|
| **Time to first short summary** | ≤ **15s** for ≤10‑min video with captions | Timestamp logs (`progress.short_ready_at - ingest_at`) |
| **End‑to‑end latency** | ≤ **60s** for ≤30‑min captioned video | `result_ready_at - ingest_at` |
| **Success rate** | ≥ **95%** (no manual retry) | Job outcomes over golden set runs |
| **Cost per 10‑min video** | ≤ **¥2–¥10** | Token usage × provider rates; internal estimator |
| **Cache hit rate** | ≥ **50%** on repeat runs | `cache_hit=true` counter |
| **Timestamp accuracy** | Within **±5s** | Spot‑check 10 links per run |

---

## 5) Test Cases (Functional)

### Legend
- **P0** = must pass to ship; **P1** = should pass; **P2** = nice to have.

| ID | Title | Steps | Expected | Priority |
|---|---|---|---|---|
| TC‑URL‑001 | URL validation (valid) | Enter `https://youtube.com/watch?v=ID` → Process | Error hidden; job created | P0 |
| TC‑URL‑002 | URL validation (invalid) | Enter `hello world` → Process | Inline error in <200ms | P0 |
| TC‑CAP‑003 | Captions path (happy) | Use video with captions | Progress shows; results tabs filled | P0 |
| TC‑CAP‑004 | No captions → ASR prompt | Video without captions | ASR modal shown; “Enable & Continue” proceeds | P0 |
| TC‑DUR‑005 | Duration limit | Video >90 min | Friendly error; allow override only if setting on | P0 |
| TC‑QUE‑006 | Queueing | 4th job concurrently | Job queued; ETA shown; can cancel | P1 |
| TC‑TIM‑007 | Timestamp links | Click timestamp chip | Opens YouTube at ±5s offset | P0 |
| TC‑MD‑008 | Markdown export | Click “Download .md” | File matches on‑screen content | P0 |
| TC‑HIS‑009 | History open | Process twice → open from History | Loads cached artifacts, no recompute | P1 |
| TC‑HIS‑010 | History delete | Delete an item | Removed from list, storage unaffected | P2 |
| TC‑ERR‑011 | Private/members‑only | Use private video ID | Clear error; no processing attempt | P0 |
| TC‑ERR‑012 | Deleted/blocked | Use removed/geo‑blocked | Clear error; suggests retry/alt | P1 |
| TC‑I18N‑013 | Japanese captions | JA video | Outputs readable JA; encoding OK | P1 |
| TC‑QUAL‑014 | Coverage quality | Golden set item | Passes rubric ≥4/5 avg | P0 |
| TC‑BUD‑015 | Budget guardrail | Force low token cap | App degrades (fewer bullets) vs failing | P1 |
| TC‑RET‑016 | Partial summary early | ≤10‑min captioned | Short summary in ≤15s | P0 |
| TC‑ACC‑017 | Keyboard navigation | Tab across UI | Focus visible; Enter activates; ARIA labels present | P1 |
| TC‑SRCH‑018 | Transcript search | Search keyword | Highlights found lines; clears on empty | P2 |

---

## 6) API Tests

Use `pytest` + `httpx` or `pytest` + `requests`:

### `/ingest`
- **200** with `{job_id}` for valid public video.
- **400** for invalid URL.
- **409** if identical job already running (optional).

### `/status/{job_id}`
- Progress transitions: `queued → running → done|error` with `stage` (validate order).

### `/result/{job_id}`
- **200** with schema:
  ```json
  {
    "video": {"title":"", "channel":"", "duration": 0, "url": ""},
    "sections": {"short":"", "detailed":[], "ideas":[], "takeaways":[]},
    "links": {"markdown":"", "transcript_json": ""}
  }
  ```
- **404** if job unknown/expired.
- Ensure artifacts exist at `links.*`.

**Negative tests:**
- Private/removed IDs → 4xx with helpful message.
- Over‑duration → 4xx with limit guidance.

---

## 7) Unit & Integration Tests

### Unit (examples)
- `test_chunker_token_boundaries.py` — chunk sizes and overlaps.
- `test_time_utils.py` — `mm:ss`/`hh:mm:ss` → seconds + back.
- `test_markdown_exporter.py` — parity with DOM sample.
- `test_cache_key.py` — hash stability over identical input.
- `test_url_validation.py` — common YT URL forms.

### Integration
- `test_transcript_normalization.py` — captions → segments (fixtures).
- `test_pipeline_map_reduce.py` — mocked LLM returns; dedupe + ordering.
- `test_budget_guardrail.py` — force token cap; expect graceful degrade.
- `test_queueing_flow.py` — simulate >3 concurrent jobs.

---

## 8) Manual QA — Golden Set Rubric

Score each run **1–5** (5 best) on:

| Dimension | Guideline |
|---|---|
| **Coverage** | Captures major topics; minimal omissions. |
| **Correctness** | No hallucinated facts; aligns with transcript. |
| **Actionability** | Takeaways are concrete and useful. |
| **Readability** | Clear, concise, well‑structured Markdown. |
| **Timestamping** | Key ideas map to correct moments (±5s). |

**Pass criteria per video:** average ≥ **4.0** and no dimension < **3.**  
Record in `/tests/golden_results.csv` with columns: `video_id,title,coverage,correctness,actionability,readability,timestamps,notes`.

---

## 9) Acceptance Criteria (Ship Gate)

- For ≤10‑min captioned videos (golden set):
  - **Short summary in ≤15s**; **full output in ≤60s** (median).
  - **Success rate ≥95%** (no manual retry).
  - **Quality ≥4/5** average on rubric.
- For repeat runs on same `transcript_hash`:
  - **Cache hit** observed and recompute skipped.
- Markdown export exactly mirrors UI sections.

---

## 10) Accessibility & Usability Checks

- Keyboard: Tab order logical; focus rings visible; Enter/Space activate tabs.
- ARIA: tabs use `role="tablist"/"tab"/"tabpanel"` with labels and `aria-controls`.
- Color contrast: all text ≥ WCAG AA on dark background.
- Responsive: min width 360px; content readable; no horizontal scroll.

---

## 11) Security/Privacy Checks

- No transcripts persisted unless explicitly enabled.
- Secrets loaded via env, never logged.
- Logs: request IDs, durations, non‑PII metadata only.
- Artifact names exclude user tokens/keys.

---

## 12) Tooling & Commands

**Python**
```bash
pytest -q
pytest -q tests/test_pipeline_map_reduce.py::test_budget_guardrail
```

**API smoke (HTTPie)**
```bash
http POST :8000/ingest url=https://youtube.com/watch?v=abc123
http GET  :8000/status/<job_id>
http GET  :8000/result/<job_id>
```

**Browser**
- Run Lighthouse accessibility check.
- DevTools throttling: “Fast 3G”.

---

## 13) Schedule & Ownership

- **When**: Aligned to roadmap phases (§Timeline).  
- **Who**: You (solo). Daily testing at end of each phase; final pass before launch.  
- **Tracking**: Issues labeled `qa`, `bug`, `perf`, `a11y` in GitHub.

---

## 14) Templates

**Bug report**
```
Title: [Component] concise problem summary
Env: browser/version, OS, build SHA
Steps:
1. ...
2. ...
Expected: 
Actual:
Artifacts: screenshots/logs/job_id(s)
Severity: S1/S2/S3  Priority: P0/P1/P2
```

**Golden set entry (JSON)**
```json
{
  "video_id": "XXXXXXXXXXX",
  "title": "Short explainer on spaced repetition",
  "channel": "Example Channel",
  "duration_seconds": 754,
  "has_captions": true,
  "language": "en"
}
```

---

## 15) Maintenance

- Keep fixtures stable; only rotate golden set when content is removed.
- Snapshot token/cost rates used for cost KPI calculations.
- Add a regression test whenever a production bug is fixed.
