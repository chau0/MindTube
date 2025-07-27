# M1 — API skeleton & run model

| ID | Title | Description | Files | Commands | DoD | Labels | TimeboxMinutes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-005 | FastAPI app skeleton | Create FastAPI app with /runs, /runs/{id}, /runs/{id}/events (stub), /healthz. | api/main.py; api/routes/runs.py | make dev; curl endpoints | OpenAPI renders; stub endpoints respond. | backend,api | 90 |
| T-006 | Run entity + SQLite store | Create runs table (SQLite) and CRUD helpers; simple migration script. | api/db.py; api/models.py; scripts/migrate.py | python scripts/migrate.py; make test | Create/read/update runs works; tests green. | backend,db | 90 |
| T-007 | SSE event stream | Implement Server-Sent Events for progress streaming. | api/sse.py; api/routes/runs.py | make dev; curl -N /runs/{id}/events | Receives periodic events for mock job. | backend,api | 60 |
| T-008 | RQ + Redis queue wiring | Wire enqueue on POST /runs; worker consumes no-op job; DLQ table. | worker/worker.py; api/queue.py; api/dlq.py | docker compose up; make dev | Job enqueued/consumed; failures land in DLQ. | backend,queue | 90 |
