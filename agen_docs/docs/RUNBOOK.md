# RUNBOOK — Ops

## Start/Stop
```bash
docker compose up -d
docker compose down
```

## Common ops
- Retry DLQ: `python cli/retry.py --run <id>`
- Check queue depth: `redis-cli LLEN rq:queue:default`
- Inspect metrics: `curl localhost:8000/metrics`

## Failure playbooks
- 429 storms: enable backoff; reduce concurrency; wait and retry.
- LLM timeouts: retry with jitter; consider switching reduce provider.
- Transcript fail: prompt user to upload SRT/VTT or enable ASR.
