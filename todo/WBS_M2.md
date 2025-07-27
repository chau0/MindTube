# M2 — Transcript sources

| ID | Title | Description | Files | Commands | DoD | Labels | TimeboxMinutes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-009 | TranscriptSource interface | Define transcripts/base.py protocol and plugin registry. | transcripts/base.py; transcripts/registry.py | make test | Plugins can register/resolve; unit tests pass. | backend,design | 60 |
| T-010 | Upload SRT/VTT endpoint | Accept .srt/.vtt and normalize to sentence-level JSON with timestamps. | api/routes/transcripts.py; transcripts/upload.py; tests/test_upload_transcript.py | make dev; pytest -k upload | Fixture SRT/VTT converts correctly. | backend,ingest | 90 |
| T-011 | Unofficial transcript (feature-flag) | Adapter for unofficial transcript retrieval, behind config flag (OFF by default). | transcripts/unofficial.py; tests/test_unofficial.py | pytest -k unofficial | Mocked HTML parsed; respects flag. | backend,ingest,risk | 90 |
| T-012 | ASR fallback (opt-in) | Whisper wrapper (local/API) with 120-minute cap and cost/time estimate. | transcripts/asr.py; tests/test_asr.py | pytest -k asr | Short sample transcribed; limit enforced. | backend,asr | 90 |
