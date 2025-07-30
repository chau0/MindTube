### Phase 1 — CLI (MVP, library‑first)

**Goals**

* Given a YouTube URL → fetch transcript (with fallbacks) → produce JSON: `{summary, main_ideas[], takeaways[], artifacts}` and save to disk.

**Suggested tech**

* **CLI:** Typer (clean UX), Rich (progress/logging).
* **HTTP/LLM:** official Gemini SDK or REST; exponential backoff.
* **Config:** pydantic-settings + `.env` (API keys, proxy).
* **Deps/Build:** `uv` (lock + sync), `make` targets, `ruff` + `pyright`, `pytest`.
* **Structure**

  ```
  ytnote/
    cli/                # Typer commands
    core/               # pure logic (no I/O): chunk, prompts, merge
    io/                 # transcripts, cache, filesystem paths
    llm/                # gemini client + guards + retries
    models/             # pydantic schemas for outputs/artifacts
    qa/                 # (prepare for phase 2) retrieval over chunks
    __init__.py
  data/
    <video_id>/
      transcript.json
      chunks.jsonl
      summary.json
      main_ideas.json
      takeaways.json
      mindmap.json      # optional
  ```

**CLI commands (library-first)**

* `ytnote fetch <url>` → `transcript.json`
* `ytnote summarize <url|video_id>` → `summary.json`
* `ytnote ideas <url|video_id>` → `main_ideas.json`
* `ytnote takeaways <url|video_id>` → `takeaways.json`
* `ytnote process <url>` → all of the above (skips steps if cache exists)
* Flags: `--lang`, `--proxy`, `--force`, `--outdir`, `--model`.

**Transcript pipeline**

1. Extract `video_id`.
2. Try `youtube-transcript-api` with requested langs; if none:
3. **Fallback A:** yt-dlp to download captions (`--write-auto-sub --sub-format vtt`) if allowed in your environment.
4. **Fallback B (optional later):** speech-to-text (whisper) on audio if captions unavailable.
5. Normalize to segments: `[ {start, end, text, lang} ]`.

**Chunking strategy (deterministic)**

* Token-aware splitting at sentence/paragraph boundaries (\~1–2k tokens per chunk).
* Store as `chunks.jsonl` with `chunk_id`, `token_estimate`, and `source_range`.

**Summarization strategy**

* **Map-reduce**:

  * **Map:** per chunk → concise chunk summary with key points.
  * **Reduce:** merge K chunk summaries into final **summary**, **main\_ideas** (bullet list with 1‑line rationales), **takeaways** (actionable).
* Keep prompts **schema-first**: ask Gemini to return **pydantic-shaped JSON** (no prose). Validate and save.

**Mind map (nice-to-have, still Phase 1-compatible)**

* Produce a neutral **graph JSON**:

  ```json
  { "root": "Topic", "nodes": [{ "id": "n1", "label": "Idea" }], "edges": [{ "from": "root", "to": "n1" }] }
  ```
* Also export **Mermaid** or **Markmap** Markdown for easy UI later.

**Makefile (targets)**

* `make setup` (uv sync)
* `make lint` (ruff + pyright)
* `make test` (pytest -q)
* `make format` (ruff format)
* `make run CMD="ytnote process <url>"`

**Caching & idempotency**

* Check for `data/<video_id>/transcript.json` etc. Skip work unless `--force`.

**Logging**

* JSON logs (structlog or standard logging with JSON formatter).
* Include `video_id`, `phase`, `step`, `duration_ms`, `token_used`.

**Phase 1 Definition of Done**

* CLI `process` runs end-to-end for 3+ test videos (with/without human captions).
* Artifacts written deterministically under `data/<video_id>/`.
* Re-running without `--force` is **no-op**.
* Unit tests: chunker, prompt builders, reducers (≥80% lines in `core/` & `models/`).
* Rate-limit/retry logic verified with fault-injection tests.

---

### Phase 2 — API wrapper (FastAPI)

**Endpoints**

* `GET /healthz`
* `POST /ingest` `{url, lang?, force?}` → returns `job_id`
* `GET /status/{job_id}` → `queued|running|done|error`
* `GET /videos/{video_id}/summary|ideas|takeaways|mindmap|transcript`
* `POST /qa` `{video_id, question}` → answer + cited chunk\_ids (prepare RAG)
* `POST /captions` `{url, lang?}` → transcript only

**Async processing**

* Start simple: `BackgroundTasks` + in-memory registry for job status.
* If concurrency/scale needed: **RQ/Redis** or **Arq** (async Redis) later without changing API surface.

**Storage**

* Keep same on-disk layout; add a light **SQLite** index (video\_id, title, duration, langs, created\_at).

**Observability**

* Request/trace ID middleware.
* Basic counters (ingests, errors) via Prometheus client (optional).

**Phase 2 DoD**

* Ingest non-blocking; can poll `status` and fetch artifacts.
* API returns **validated JSON** matching Phase 1 schemas.
* Load tests (locust) confirm no main-thread blocking for a 5‑video batch.

---

### Phase 3 — Minimal UI

**Features**

* Input URL, select language → **Process**.
* Show live status (polling or WebSocket).
* Render summary, ideas, takeaways; download transcript.
* Optional: render mind map (Mermaid/Markmap/cytoscape).

**Phase 3 DoD**

* One-click from URL to results with visible progress.
* No layout/JS errors across Chrome/Firefox.
* E2E test (Playwright) for happy path.

---

## Testing & TDD (how to make it stick)

* **Unit** (fast):

  * Chunker splits by token budget and preserves sentence boundaries.
  * Prompt builders output strict JSON schemas.
  * Reducer merges deterministically (same input → same output).
* **Integration** (LLM stub first):

  * Inject a **fake Gemini client** returning canned JSON; later swap to real client in a “live” test marker.
* **Contract**:

  * Pydantic models for artifacts; validate every LLM response.
  * Freeze test data (two short transcripts, one long).
* **CLI snapshot tests**:

  * Run `process` on a short video fixture; compare produced JSON (allow minor fields like timestamps to be ignored).
* **Negative cases**:

  * No captions, geo-blocked, empty transcript → meaningful error & exit code.

---

## Prompts (structure, not wording)

* **Map prompt** (per chunk): “Return JSON: { key\_points: \[string], summary: string, quotes?: \[string] }”.
* **Reduce prompt** (all chunk summaries): “Return JSON: { summary: string, main\_ideas: \[{idea, rationale}], takeaways: \[string] }”.
* Always request **JSON only**, no prose; retry on invalid JSON.

---

## Security & Keys

* Read keys from `.env`; never log them.
* Optional proxy: read `HTTP_PROXY/HTTPS_PROXY` or a dedicated `YT_PROXY` env var.

---

## Template options (given uv + Make)

* Keep your chosen template and replace Poetry with uv, **or** consider:

  * **cookiecutter-pypackage** (vanilla; easy to adapt to uv)
  * **copier-pdm** or a minimal **uv** project skeleton
* Whichever you pick, ensure `pyproject.toml` uses **PEP 621** (uv-friendly).

---

## Suggested next actions (1–2 days)

1. Initialize repo with **uv + Typer + pytest + ruff + pyright + Makefile**.
2. Implement **video\_id extraction, transcript fetch + cache**, and **chunker** (pure functions).
3. Stub Gemini client (returns canned JSON); implement **map-reduce** flow & JSON schemas.
4. Wire CLI `process` end-to-end using the stub → green tests → swap to real Gemini.
5. Add `--force`, `--lang`, and structured logging.

If you want, I can generate:

* A **WBS** with tasks, estimates, and DoD per task.
* A **pydantic schema** set for all outputs.
* A **Makefile** + `pyproject.toml` starter aligned to uv.
