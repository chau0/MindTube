# API Contract — Overview

See `openapi.yaml` for the full contract.

## Endpoints (MVP)
- `POST /runs` — Start a run for a YouTube URL.
- `GET /runs/{id}` — Run metadata and artifacts list.
- `GET /runs/{id}/events` — SSE progress stream.
- `GET /runs/{id}/result` — Final artifacts.
- `POST /transcript/upload` — Upload SRT/VTT to use as transcript.
- `POST /runs/{id}/cancel` — Best-effort cancel.
- `GET /healthz` — Liveness check.

Errors follow `docs/ERRORS.md` taxonomy.
