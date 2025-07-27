# OBSERVABILITY

## Logging
- JSON logs including: `runId`, `stage`, `ms`, `error_code`, `model`

## Metrics
- Counters: runs_total, runs_failed_total
- Histograms: stage_duration_ms, token_input, token_output
- Gauges: queue_depth, cache_hit_ratio

## Endpoints
- `/metrics` (Prometheus format)
- Correlate API and worker logs by `runId`
