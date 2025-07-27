# QA PLAN & BENCHMARK SET

## Benchmark set (10 videos)
- Short tutorial (<10m), long talk (30–60m), interview, coding tutorial, lecture (EN/JA).

## Scoring rubric (1–5)
- Coverage: timestamps span the video content
- Correctness: faithful to transcript
- Actionability: useful key ideas/takeaways

## Gates
- Average ≥ 4.0 on 8/10 videos
- Timestamp accuracy within ±5s on ≥80% bullets

## How to run
```bash
make e2e
pytest -k e2e
```
