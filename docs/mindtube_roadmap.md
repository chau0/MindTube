# MindTube — MVP Project Plan / Roadmap

**Version:** 2025‑07‑26 (JST)  
**Owner:** You (PM/Builder)

> **Goal:** Ship a usable MVP that ingests a YouTube URL and returns **Summary / Key Ideas / Takeaways / Transcript (downloadable .md)** with timestamp links.

---

## 1) Phases & Milestones (MVP)

### Phase 0 — Project Setup (0.5 day)
**Milestones**
- Repo initialized (frontend + backend workspaces)
- Shared env template, run scripts, lint/format

**Deliverables**
- `README`, `.env.example`, CI lint

### Phase 1 — UX Prototype & Flow (1 day)
**Milestones**
- Landing page (URL field), progress states, tabbed results
- Clickable prototype verified with dummy data

**Deliverables**
- Low‑fi UI, tab navigation, Markdown export stub

### Phase 2 — Backend Scaffold (1 day)
**Milestones**
- FastAPI project; endpoints: `/ingest`, `/status/{job_id}`, `/result/{job_id}`
- Background task runner (asyncio or Arq)

**Deliverables**
- Running API with a mock pipeline

### Phase 3 — Transcript Service (1–1.5 days)
**Milestones**
- YouTube metadata + captions fetch (official API first)
- Normalization to segments (start/end ms, text)
- ASR toggle stub (Whisper path and config)

**Deliverables**
- Transcript JSON, `transcript_hash`, basic errors

### Phase 4 — Summarization Pipeline (1.5 days)
**Milestones**
- Chunking (token‑aware), Map (mini model), Reduce (mini/standard)
- Timestamped bullets, budget guardrails, retries

**Deliverables**
- JSON sections (short, detailed[], ideas[], takeaways[])

### Phase 5 — Frontend Integration (0.5–1 day)
**Milestones**
- Connect UI → API; show partial results; timestamp links open in YouTube
- Markdown export parity with UI

**Deliverables**
- End‑to‑end run for ≤10‑min captioned video

### Phase 6 — Caching, History, Errors (0.5 day)
**Milestones**
- Cache by `video_id + transcript_hash + params`
- Local history (last 20); friendly error states

**Deliverables**
- No duplicate recompute; clear UX for edge cases

### Phase 7 — Testing & Quality Pass (0.5–1 day)
**Milestones**
- Golden set (10–15 videos) manual eval
- Unit tests for chunker/markdown; integration smoke tests

**Deliverables**
- Test report; buglist triage

### Phase 8 — Launch Prep (0.5 day)
**Milestones**
- Deploy (small VPS/Render/Fly) or local‑only package
- Usage notes, cost/latency notes, known issues

**Deliverables**
- MVP “Go Live” checklist, version tag

---

## 2) Timeline (Realistic, MVP)

**Fast‑track (7–8 days total)**

| Phase | Dates (JST) | Duration |
|---|---|---|
| 0. Setup | Sun **Jul 27** (AM) | 0.5 day |
| 1. UX Prototype | Sun **Jul 27** (PM) | 0.5 day |
| 2. Backend Scaffold | Mon **Jul 28** | 1 day |
| 3. Transcript Service | Tue **Jul 29** – Wed **Jul 30** (AM) | 1–1.5 days |
| 4. Summarization Pipeline | Wed **Jul 30** (PM) – Thu **Jul 31** | 1.5 days |
| 5. FE Integration | Fri **Aug 1** (AM) | 0.5 day |
| 6. Cache/History/Errors | Fri **Aug 1** (PM) | 0.5 day |
| 7. Testing & Quality | Sat **Aug 2** | 0.5–1 day |
| 8. Launch Prep | Sun **Aug 3** (AM) | 0.5 day |

**Go/No‑Go:** Ship MVP by **Sun Aug 3, 2025** if acceptance criteria are met.  
**Conservative plan:** add 2–3 buffer days across Phases 3–4 and 7 → Launch by **Aug 5–6**.

---

## 3) Team Roles & Responsibilities

> You’re currently solo. Below maps responsibilities; if you add collaborators, use it as a RACI.

| Area | Tasks | Owner (RACI) |
|---|---|---|
| Product/UX | Flows, copy, acceptance criteria | **You (R)** |
| Frontend | Next.js UI, tabs, progress, export, history | **You (R)** |
| Backend/API | FastAPI endpoints, job orchestration | **You (R)** |
| Transcript | YouTube API integration, normalization, ASR toggle | **You (R)** |
| Summarization | Chunker, map/reduce prompts, token budget | **You (R)** |
| Infra/Deploy | Dev/prod env, logs, simple monitoring | **You (R)** |
| QA | Golden set evaluation, latency/cost checks | **You (R)** |

_RACI key_: **R**esponsible, **A**pprover (You), **C**onsulted (—), **I**nformed (—).

---

## 4) Communication Plan

- **Daily log (10 min, end of day):** What moved, blockers, tomorrow’s target.  
  - Tool: GitHub Projects note or a `/docs/DAILY.md` append.
- **Issue tracking:** One GitHub issue per milestone with acceptance checklist.  
  - Labels: `frontend`, `backend`, `transcript`, `summarization`, `infra`, `qa`.
- **Branching:** `main` (stable), `dev` (integration), feature branches `feat/<scope>`.
- **Release cadence:** Tag MVP `v0.1.0` on launch; changelog in `CHANGELOG.md`.
- **Metrics check‑ins (every other day):** latency (10‑min video), tokens/run, completion %, cache hit rate.

If you add collaborators:
- **Async first:** Discord/Slack channel + weekly 30‑min sync.
- **PRs:** template with “scope, screenshots, test notes”.

---

## 5) Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Captions unavailable / blocked | Med | Med | Clear UX to enable ASR; duration cap; defer ASR to Post‑MVP if needed; log frequency. |
| YouTube API quota / ToS changes | Low‑Med | Med‑High | Use official API; cache results; expose API key; graceful degradation; monitor quota. |
| LLM cost creep | Med | Med | Map on mini; reduce on std under budget; max tokens/run; cache by `transcript_hash`. |
| Latency too high on long videos | Med | Med | Early partial summary; tune chunk size; parallelize map; show ETA; cap length (≤90 min). |
| Hallucinations / coverage gaps | Med | Med | Prompt constraints; rubric QA; timestamp references. |
| Worker/queue instability | Low | Med | Start with `BackgroundTasks`; move to Arq/Redis if needed; retry idempotently. |
| Storage/data leaks | Low | High | Local‑only by default; dotenv configs; no transcript retention without opt‑in. |
| ASR compute/time blowout | Med | Med | Whisper small/medium; strict duration limit; async offload; opt‑in only. |

---

## 6) Milestone Acceptance Criteria

- **Phase 1 → 2:** Prototype shows tabs + dummy results; Markdown export works.
- **Phase 2 → 3:** `/ingest` returns `job_id`; `/status` progresses; `/result` returns mock sections.
- **Phase 3 → 4:** Real captions normalize to segments; errors for private/members‑only videos; stable `transcript_hash`.
- **Phase 4 → 5:** For ≤10‑min video with captions, pipeline returns all sections with timestamps; total runtime ≤ 15s on dev rig (or documented).
- **Phase 5 → 6:** UI renders real results; timestamp links open YouTube at ±5s; `.md` mirrors UI content.
- **Phase 6 → 7:** Cache prevents recompute; friendly errors (no captions, too long, rate limit).
- **Phase 7 → 8:** Golden set scores ≥ 4/5 on coverage/correctness/actionability; success rate ≥ 95%.

---

## 7) Tracking & Reporting

**KPIs (MVP)**
- Time to short summary ≤ 15s (≤10‑min video w/ captions)
- End‑to‑end ≤ 60s (≤30‑min video)
- Success (no manual retry) ≥ 95%
- Cost within budget (¥2–¥10 per 10‑min video)

**Artifacts**
- `/docs/roadmap.md` (this plan)
- `/docs/test-plan.md` (golden set + rubric)
- `/docs/ops.md` (env vars, runbook)
