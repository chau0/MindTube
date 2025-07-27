# MindTube — Work Breakdown Structure (Phase-Ordered)
**Version:** 2025-07-27

## Phase 1 — CLI MVP
| ID | Task | DoD | How to Check |
|---|---|---|---|
| 1.1 | Repo scaffold & tooling | CLI runs `--help`; linters clean | `make install && mindtube --help`; `ruff`, `mypy` |
| 1.2 | Config system | Env/flags load with `--debug` | `mindtube --debug` shows endpoint/model/langs |
| 1.3 | URL parsing | Handles youtube.com/youtu.be variants | Unit tests for variants green |
| 1.4 | Caption fetch | `transcript.jsonl` saved | File exists; >20 lines; valid JSONL |
| 1.5 | ASR fallback | Produces transcript when captions missing | Use `--force-asr`; check log path |
| 1.6 | Normalization | Clean text; mm:ss timestamps | Spot-check samples |
| 1.7 | Chunking | ≤ token limit; full time coverage | Unit + property tests |
| 1.8 | LLM adapter (Azure) | `generate()` ok; retries/backoff | Contract test + simulated 429 |
| 1.9 | Map step | Per-chunk JSON schema valid | Validate against `schemas/map.json` |
| 1.10 | Reduce step | `summary.json` valid | Validate `schemas/reduced.json` |
| 1.11 | Exporters | `notes.md`, `mindmap.mmd` | Files exist; preview Mermaid |
| 1.12 | Cache/history | Cache hit on repeat runs | 2nd run faster; DB row present |
| 1.13 | CLI UX | Flags & progress bars | Manual run with flags |
| 1.14 | E2E test | Short video end-to-end | `pytest -k e2e_cli` passes |
| 1.15 | Cost guards | Max duration & token budgets | Long video shows guard message |

## Phase 2 — Hardening
| ID | Task | DoD | How to Check |
|---|---|---|---|
| 2.1 | Error taxonomy | Specific exceptions + messages | Forced failures map to right class |
| 2.2 | JSON schemas | Enforced at boundaries | Invalid JSON → clear error |
| 2.3 | Determinism | Temp=0; prompt versioning | Re-run similar TL;DR; version stored |
| 2.4 | Logging/metrics | Log per stage + token costs | Inspect `run.log.jsonl` |
| 2.5 | Mindmap pruning | Depth/breadth caps | Mermaid renders cleanly |
| 2.6 | Tests | Unit + snapshots | `pytest` all green |
| 2.7 | Docs | README + troubleshooting | Fresh setup succeeds |

## Phase 3 — API
| ID | Task | DoD | How to Check |
|---|---|---|---|
| 3.1 | Scaffold | `/healthz` 200 | `curl` |
| 3.2 | POST /runs | Returns `run_id` & status | `curl -X POST` |
| 3.3 | Runner | Background execution | queued→running→done in logs |
| 3.4 | GET /runs/{id} | Status/progress | Polling shows progress |
| 3.5 | Artifacts | Download links | Files downloadable |
| 3.6 | Static serving | Correct MIME | Browser renders MD/JSON |
| 3.7 | API key | Enforced | Missing key ⇒ 401 |
| 3.8 | Docker | Containerized app | `docker compose up` ok |
| 3.9 | Rate limit (opt) | 429 on abuse | Exceed threshold ⇒ 429 |

## Phase 4 — Frontend
| ID | Task | DoD | How to Check |
|---|---|---|---|
| 4.1 | Form | Submits URL to API | `.env.local` + submit works |
| 4.2 | Polling | Status updates | Visual progress |
| 4.3 | Render tabs | MD/JSON/Mermaid display | Tabs render cleanly |
| 4.4 | Copy/Download | Actions work | Buttons function |
| 4.5 | UX polish | Errors/empty states | Simulate errors |

## Phase 5 — Scale/Polish (Optional)
| ID | Task | DoD | How to Check |
|---|---|---|---|
| 5.1 | Workers/Queue | DLQ + retries | Kill worker → retries |
| 5.2 | Object storage | Artifacts externalized | URLs from Blob/B2 |
| 5.3 | Concurrency limits | Stable latency under load | Load test |
| 5.4 | Observability | Dashboards | Metrics visible |
| 5.5 | Provider swap | Config change only | E2E passes; cost ↓ |
