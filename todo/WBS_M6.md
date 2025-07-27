# M6 — Hardening & release

| ID | Title | Description | Files | Commands | DoD | Labels | TimeboxMinutes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-029 | Rate limit gates | Queue concurrency caps; 429 backoff; DLQ retry command. | worker/concurrency.py; cli/retry.py | python cli/retry.py --run <id> | Backoff triggers on mock 429; retry works. | backend,reliability | 60 |
| T-030 | E2E smoke suite | Three sample videos (short/long/lecture) run end-to-end locally. | tests/e2e/* | make e2e | All three pass within latency caps. | testing,e2e | 90 |
| T-031 | Docs | README with setup; constraints; ToS; privacy; limits; troubleshooting. | README.md; docs/* |  | New contributor can run MVP in <15 minutes. | docs | 60 |
