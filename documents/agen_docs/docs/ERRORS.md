# ERROR TAXONOMY

| Code | HTTP | Message (UI) | Auto Action |
|---|---:|---|---|
| VIDEO_UNAVAILABLE | 400/404 | This video isn’t accessible. | Stop |
| CAPTIONS_NOT_FOUND | 200 | No captions found. Enable ASR to proceed. | Offer ASR |
| ASR_DISABLED | 200 | ASR is off. | Stop |
| ASR_LENGTH_LIMIT | 200 | Video too long for ASR (max 120m). | Stop |
| RATE_LIMIT | 429 | Temporarily rate limited; retrying… | Backoff+retry |
| LLM_TIMEOUT | 504 | Model timed out; retrying… | Retry w/ jitter |
| LLM_VALIDATION_FAIL | 500 | Output validation failed. | Corrective pass |
| INTERNAL | 500 | Something went wrong. | DLQ + alert |
