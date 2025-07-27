# MindTube — Architecture Design (MVP)

**Version:** 2025‑07‑27 (JST)  
**Owner:** You (PM/Builder)  
**Status:** Draft for implementation

---

## Table of Contents
- [1. Goals & Non‑Goals](#1-goals--non-goals)
- [2. System Context](#2-system-context)
- [3. High‑Level Architecture](#3-high-level-architecture)
- [4. Component Responsibilities](#4-component-responsibilities)
- [5. End‑to‑End Data Flow](#5-end-to-end-data-flow)
- [6. Pipeline Design](#6-pipeline-design)
- [7. Data Model & Storage](#7-data-model--storage)
- [8. API Surface](#8-api-surface)
- [9. Caching & Cost Controls](#9-caching--cost-controls)
- [10. Observability](#10-observability)
- [11. Security, Privacy & Compliance](#11-security-privacy--compliance)
- [12. Error Taxonomy & Handling](#12-error-taxonomy--handling)
- [13. Deployment & Environments](#13-deployment--environments)
- [14. Sizing Targets & SLOs](#14-sizing-targets--slos)
- [15. Risks, Obstacles & Mitigations](#15-risks-obstacles--mitigations)
- [16. Testing Strategy](#16-testing-strategy)
- [17. Roadmap & Extensions](#17-roadmap--extensions)

---

## 1. Goals & Non‑Goals

### Goals
- Paste a YouTube URL → get **timestamped summary**, **key ideas**, and **takeaways** quickly and reliably.
- Support **EN/JA** transcripts first; accurate timestamp alignment; clear UX with progress and retry.
- Keep **latency, quality, and cost** balanced via map‑reduce and caching.
- Operate safely within **YouTube ToS** using official APIs for captions; ASR only on **opt‑in**.

### Non‑Goals (MVP)
- No batch processing, multi‑user accounts, or collaboration.
- No automatic Notion/Drive sync (export is manual).
- No scraping of protected/member/age‑restricted content.
- No permanent cloud retention by default (local history in browser only).

---

## 2. System Context

```mermaid
flowchart LR
  U[User] --> FE[Next.js Frontend]
  FE -->|Start Run| API[FastAPI API]
  API --> Q[Redis Queue]
  Q --> ING[Transcript Ingestor]
  ING -->|captions.download| YT[YouTube Data API]
  Q --> PIPE[Summarizer Pipeline]
  PIPE --> LLM[LLM Provider(s)]
  PIPE --> C[(Redis Cache)]
  API --> DB[(Postgres: metadata)]
  PIPE --> S3[(Object Storage: artifacts)]
  API -- SSE/WebSocket --> FE
  FE -- Download/Copy --> S3
```

**Context notes**
- API remains stateless; heavy work executes in workers subscribed to the queue.
- Ingestor isolates ToS‑sensitive flows; Pipeline focuses on chunking and summarization.
- Artifacts (captions/transcript/chunks/summary) are persisted to object storage; DB holds metadata.

---

## 3. High‑Level Architecture

- **Frontend:** Next.js (TypeScript, App Router, shadcn/ui). Uses **SSE** for live progress and keeps a local history (IndexedDB) with export/import JSON.
- **API:** FastAPI + Pydantic, exposes `/runs` and SSE endpoint for progress. Idempotent run creation.
- **Queue/Workers:** Celery or RQ with Redis. Concurrency limits per stage; dead‑letter queue for failed jobs.
- **Transcript Ingestor:** Official YouTube Data API (`captions.list`, `captions.download`). Optional **Whisper ASR** for cases without captions (user opt‑in, 120‑minute cap).
- **Summarizer Pipeline:** Map‑reduce approach with JSON‑schema prompts; mini model for map stage, higher‑quality model for reduce stage.
- **Cache:** Redis using deterministic keys to deduplicate work across identical requests.
- **Storage:** Postgres for runs/metrics; S3/MinIO for large artifacts.
- **Observability:** Structured logs, metrics (Prometheus/Grafana), request/run IDs, and minimal tracing.

---

## 4. Component Responsibilities

### Frontend (Next.js)
- Input validation, run creation, SSE stream consumption, UI tabs (Summary, Key Ideas, Takeaways, Transcript).
- Local history: store last 20 runs (videoId, title, date, summary link) in IndexedDB.
- Accessibility: keyboard focus, ARIA labels, readable line length.

### API (FastAPI)
- Validate YouTube URL; create run; return `runId`.
- Publish run to queue; stream progress (SSE) with `{stage, pct, eta, message}`.
- Expose result endpoints and presigned URLs for artifacts.

### Queue & Workers
- **Ingestor Worker:** Retrieve captions via YouTube API (with user‑provided API key if applicable). Normalize and sentence‑timestamp transcript. Optionally run ASR when enabled.
- **Pipeline Worker:** Chunk transcript, run map summarization per chunk, reduce/merge results, produce Markdown + JSON artifacts, write metrics.

### Cache (Redis)
- Store prior artifacts keyed by video + params to make identical requests **instant**.

### Storage
- **Postgres:** run metadata, metrics, error codes.
- **S3/MinIO:** artifacts (`/artifacts/{runId}/{stage}.json|md`).

---

## 5. End‑to‑End Data Flow

```mermaid
sequenceDiagram
  participant FE as Frontend
  participant API as FastAPI
  participant Q as Queue
  participant ING as Ingestor
  participant SUM as Summarizer
  participant LLM as LLM Provider
  participant DB as Postgres/S3

  FE->>API: POST /runs {youtubeUrl, opts}
  API->>DB: insert run(status=QUEUED)
  API->>Q: enqueue(runId)
  API-->>FE: 202 Accepted {runId}

  FE->>API: GET /runs/{id}/events (SSE)
  Q->>ING: fetch captions/transcript
  ING->>DB: save transcript artifact
  ING-->>Q: ok

  Q->>SUM: chunk + map-reduce
  SUM->>LLM: summarize(chunk i)
  LLM-->>SUM: bullets+timestamps (JSON)
  SUM->>DB: save partials and merged outputs
  SUM-->>API: progress events

  API-->>FE: progress updates
  Q->>DB: finalize run(status=SUCCEEDED/FAILED)
  FE->>API: GET /runs/{id}/result
```

---

## 6. Pipeline Design

**6.1 Transcript Normalization**
- Merge caption lines; sentence segmentation (spaCy/BLING FIRE).  
- Maintain sentence‑level `start_ms`, `end_ms`; detect language (fastText/cld3).

**6.2 Chunking Strategy**
- Aim for ~1.5–2k tokens per chunk.
- Align boundaries to sentence/timestamps to avoid mid‑sentence splits.
- Attach chunk metadata: sentence indices, time window, token counts.

**6.3 Map Stage (fast model)**
- JSON schema response: `{ bullets:[{ ts:"mm:ss", text, quote? }], coverage: {start,end} }`.
- Low temperature; prompt forbids speculation; require timestamps and optional supporting quotes.

**6.4 Reduce Stage (higher‑quality model)**
- Consolidate bullets by time; dedupe; ensure coverage spread across video.
- Produce: **Summary (markdown)**, **Key Ideas**, **Takeaways**, each with timestamp anchors.

**6.5 Validation & Guardrails**
- Coverage check: percentage of the video spanned by bullets.
- Hallucination check: lexical overlap between quotes and transcript window.
- Length bounds: min/max bullets per 10 minutes.
- If validation fails, run a corrective prompt or mark `LLM_VALIDATION_FAIL`.

---

## 7. Data Model & Storage

### 7.1 Tables (Postgres)
- **videos**(id, youtube_id, title, duration_sec, lang, created_at)
- **runs**(id, video_id, status, started_at, finished_at, model_map, model_reduce, prompt_version, params_json, error_code, cost_cents)
- **artifacts**(id, run_id, kind, path, bytes, sha256, created_at)  
  `kind ∈ {captions, transcript, chunks, map_partials, summary_md, summary_json}`
- **metrics**(id, run_id, stage, ms, token_input, token_output, model, created_at)

**Indexes:** `(video_id)`, `(status, started_at DESC)`, `(run_id, kind)`.

### 7.2 Object Storage (S3/MinIO)
- Layout: `/artifacts/{runId}/{step}.{json|md}`
- Versioning on; integrity via SHA‑256.

---

## 8. API Surface

- `POST /runs` → `202 {runId}`  
  Body: `{ youtubeUrl, opts: { useAsr?: boolean, outputLang?: "auto"|"en"|"ja", modelTier?: "fast"|"hq" } }`

- `GET /runs/{id}` → `{ status, startedAt, finishedAt, errorCode?, artifacts[] }`

- `GET /runs/{id}/events` (SSE) → events like:  
  `{ stage: "INGEST|MAP|REDUCE|FINALIZE", pct, eta, message }`

- `GET /runs/{id}/result` → `{ summaryMd, summaryJson, links:{md,json} }`

- `POST /runs/{id}/cancel` → `{ ok: true }` (best‑effort)

- `GET /healthz`, `GET /readyz`

**HTTP Codes:** 202 (accepted), 200 (ok), 400/404 (bad url/run not found), 409 (duplicate conflicting state), 429 (rate limit), 5xx (server/provider errors).

---

## 9. Caching & Cost Controls

- **Cache key:** `videoId|lang|modelTier|promptVer|chunkingParams`  
- **TTL:** 7–30 days (configurable); invalidate on prompt/model change.
- **Re‑use:** If cache hit, skip pipeline and return prior artifacts immediately.
- **Token budgets:** strict per‑chunk/input hard caps; early‑stop if >N chunks.
- **Two‑tier modeling:** fast model for map; HQ only for final reduce.

---

## 10. Observability

- **Logging:** JSON (uvicorn/worker) with `runId`, `videoId`, `stage`, `latency_ms`, `error_code`.
- **Metrics:** per‑stage latency, token spend, hit/miss ratio, queue depth, 429 rate.
- **Dashboards:** P50/P90 latencies; error budget burn; cost/run.
- **Tracing:** optional OpenTelemetry; at minimum propagate `x-run-id` header and set MDC in workers.

---

## 11. Security, Privacy & Compliance

- **ToS:** Use only official YouTube caption endpoints; **no scraping** of protected/member/age‑restricted content.
- **ASR:** Only on explicit user opt‑in; cap to 120 minutes of audio.
- **Data retention:** No persistent server‑side storage by default beyond artifacts for the current run; browser maintains local history (exportable JSON).
- **Secrets:** Never log API keys; store user‑provided keys client‑side (secure storage) with “forget key” control.
- **PII:** Avoid storing user identifiers; rotate logs; scrub URLs in logs if necessary.

---

## 12. Error Taxonomy & Handling

| Code | Description | User Message | Auto Action |
|---|---|---|---|
| VIDEO_UNAVAILABLE | Deleted/private/region/age/members | “This video isn’t accessible.” | Stop |
| CAPTIONS_NOT_FOUND | No captions available | “No captions found. Enable ASR to proceed.” | Offer ASR |
| ASR_DISABLED | User didn’t allow ASR | “ASR is off.” | Stop |
| ASR_LENGTH_LIMIT | Audio exceeds limit | “Video too long for ASR (max 120m).” | Stop |
| RATE_LIMIT | 429 from provider | “Temporarily rate limited; retrying…” | Backoff+retry |
| LLM_TIMEOUT | Provider timeout | “Model timed out; retrying…” | Retry w/ jitter |
| LLM_VALIDATION_FAIL | Output failed checks | “Output validation failed.” | Corrective pass |
| INTERNAL | Unexpected error | “Something went wrong.” | DLQ + alert |

---

## 13. Deployment & Environments

### MVP (single host, Docker Compose)
- Services: `frontend`, `api`, `worker`, `redis`, `postgres`, `minio`.
- Backups: nightly Postgres dump; MinIO versioning on.
- CI/CD: GitHub Actions → build images, run tests, deploy via SSH or registry pull.

### Scale‑up Path
- Managed Postgres/Redis; object storage (S3); add worker replicas.
- CDN for static frontend; presigned S3 links for artifact downloads.

---

## 14. Sizing Targets & SLOs

- **Latency targets:** P50 short video (<15m) ≤ 20s; P90 ≤ 60s.
- **Reliability:** ≤ 2% failed runs (7‑day rolling).
- **Throughput (MVP):** 3 concurrent runs; queue length alarm at >10.
- **Cost goal:** ¥2–¥10 per 10 minutes of video processed.

---

## 15. Risks, Obstacles & Mitigations

1. **ToS‑compliant caption access** — Use official APIs; require user key if needed; explicit unsupported list; feature flag alternatives.
2. **Timestamp fidelity** — Sentence‑level timestamps; clamp to windows; enforce timestamps in prompts; UI ±5s “nudge” control.
3. **Cost/latency blow‑ups** — Token caps; map(mini)→reduce(HQ) cascade; aggressive caching; per‑run cost logging with alerts.
4. **Hallucinations** — Quotes+timestamps prompts; overlap checks; corrective pass if low overlap.
5. **429 storms/timeouts** — Global retry policy with exponential backoff; circuit breakers; DLQ and operator alerts.
6. **Multilingual complexity** — Auto‑detect language; `outputLang` switch; translate **final** artifacts only.

---

## 16. Testing Strategy

- **Unit:** chunker, timestamp clamp, prompt builders, validators.
- **Integration:** end‑to‑end run with mocked YouTube/LLM; record/replay fixtures.
- **Benchmark suite:** 10‑video canonical set; score coverage/correctness/actionability (≥4/5 gate).
- **Load smoke:** 5 concurrent runs of 10–15m videos; track P50/P90 and 429 handling.
- **Security:** secrets not in logs; deny unknown domains; dependency SBOM scan.

---

## 17. Roadmap & Extensions

- Chapter‑aware summaries; markmap/mermaid mind‑map exports.
- Offline/PWA mode; mobile layout polish.
- Model A/B switch; “re‑run with HQ model” button.
- Multi‑provider fallback; cost optimizer choosing best tier per video.
- Optional user accounts with server‑side history and quotas.

---

**Appendix A — Configuration (env)**
```
APP_ENV=dev
YOUTUBE_API_KEY=...
LLM_PROVIDER=openai|anthropic|google
LLM_TIER_MAP=mini
LLM_TIER_REDUCE=hq
REDIS_URL=redis://redis:6379/0
DATABASE_URL=postgresql://user:pass@postgres:5432/mindtube
S3_ENDPOINT_URL=http://minio:9000
S3_BUCKET=mindtube-artifacts
ASR_ENABLED=false
ASR_MAX_MINUTES=120
CACHE_TTL_DAYS=14
CONCURRENCY_WORKERS=3
```
