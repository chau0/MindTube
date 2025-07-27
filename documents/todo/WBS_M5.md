# M5 — Observability, errors, cost

| ID | Title | Description | Files | Commands | DoD | Labels | TimeboxMinutes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-025 | Structured logging + run-id | JSON logs include runId, stage, ms, error_code across API/worker. | api/logging.py; worker/logging.py | make dev; tail logs | Correlated logs visible for one run. | backend,observability | 60 |
| T-026 | Metrics endpoint | Expose /metrics with per-stage timers, token counts, cache hit rate. | api/metrics.py; worker/metrics.py | curl /metrics | Counters/histograms increment during run. | backend,observability | 90 |
| T-027 | Error taxonomy implementation | Map failure modes to codes; user-facing messages; retries with backoff. | api/errors.py; worker/retry.py; web/src/lib/errors.ts | make test | Injected failures show correct messages & backoff. | backend,quality | 90 |
| T-028 | Per-run cost logging | Estimate tokens × provider rate; warn if > target; save in runs.cost_cents. | api/costs.py; worker/costs.py | pytest -k costs | Cost shows in /runs; warning logged above threshold. | backend,costs | 60 |
