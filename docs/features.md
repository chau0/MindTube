# MindTube — MVP Feature List

**File:** /docs/features.md  
**Version:** v0.1 (2025‑07‑26, JST)  
**Owner:** You (PM/Builder)

This table captures all MVP‑scoped features, each with a unique ID, description, priority, and the split work across **API**, **Backend (BE)**, and **Frontend (FE)**.  
> Priority legend: **P0 = must‑have for MVP**, **P1 = nice‑to‑have in MVP window**, **Post = post‑MVP backlog**.

| ID | Feature Name | Description | Priority | API Task(s) | Backend Task(s) | Frontend Task(s) |
|----|--------------|-------------|----------|-------------|-----------------|------------------|
| F‑001 | URL Ingestion & Validation | Accept YouTube URL, validate, create job | P0 | `POST /ingest` schema & validation | URL parser, job creation, dedupe | Landing form, inline errors |
| F‑002 | Video Metadata & Captions Fetch | Resolve video metadata and fetch captions via YouTube API | P0 | — (internal) | YouTube client, quota/error mapping | Progress step “Fetching captions” |
| F‑003 | Transcript Normalization | Normalize captions to segments, compute hash | P0 | — | Normalizer, language detect, store JSON | Transcript renderer |
| F‑004 | Summarization Pipeline (Map/Reduce) | Chunk transcript, map on mini model, reduce to final sections | P0 | `/status`, `/result` schema | Chunker, orchestrator, model wrapper, retries | Tabs: Summary, Key Ideas, Takeaways |
| F‑005 | Timestamp Linking | Append &t=Ss to timestamps on bullets | P0 | — | Timestamp utility | Clickable chips in UI |
| F‑006 | Results UI Tabs | Display Summary / Key Ideas / Takeaways / Transcript | P0 | — | — | Tab component with ARIA, keyboard nav |
| F‑007 | Markdown Export | Copy/download Markdown mirroring UI | P0 | (opt) link to artifact | Markdown composer (opt server) | Buttons: Copy, Download |
| F‑008 | Progress & Partial Output | Show stage progress & early short summary | P0 | `/status` progress fields / SSE | Partial reduce path, ETA estimator | Progress widget, early summary box |
| F‑009 | Error States & Limits | Friendly errors: invalid URL, private, too long, etc. | P0 | Standardized error payloads | Duration cap, permission detection | Modal/error banners |
| F‑010 | Caching & Idempotency | Skip recompute on same transcript hash | P0 | (flag in `/status`) | Cache lookup, artifact reuse, lock | “Loaded from cache” badge (opt) |
| F‑011 | Local History | Last 20 runs stored locally, open/delete | P1 | — | — | History drawer UI |
| F‑012 | Transcript Search | Client‑side find & highlight in transcript | P1 | — | — | Search bar, highlight logic |
| F‑013 | Settings Panel | Language, duration cap, ASR default, budget guardrail | P1 | Accept params in `/ingest` | Respect params, budget enforcement | Settings modal, local storage |
| F‑014 | ASR Fallback (Whisper) | Opt‑in speech‑to‑text when no captions | P1 (compute) | `asr` flag in `/ingest` | Whisper worker, audio extract, cap duration | Prompt toggle, progress update |
| F‑015 | Observability & Metrics | Logs, token counts, basic dashboard | P1 | `/metrics` (dev) | Structured logging, counters | — |
| F‑016 | Queueing & Concurrency Control | Limit to 3 concurrent jobs, queue others | P1 | Queue info in `/status` | Semaphore queue, cancel handler | Queued state, cancel button |

---

## Change Log
| Date | Version | Notes |
|------|---------|-------|
| 2025‑07‑26 | 0.1 | Initial feature list (MVP) |

