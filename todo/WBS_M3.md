# M3 — Pipeline & LLM

| ID | Title | Description | Files | Commands | DoD | Labels | TimeboxMinutes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-013 | Sentence segmentation + timestamps | Deterministic splitter preserving start_ms/end_ms; EN/JA fixtures. | pipeline/segment.py; tests/test_segment.py | pytest -k segment | Fixtures pass; boundaries correct. | backend,pipeline | 90 |
| T-014 | Chunker with token budgeting | Chunk by ~1.5–2k tokens, align on sentences; include token counts. | pipeline/chunker.py; tests/test_chunker.py | pytest -k chunker | Chunk sizes within bounds; no mid-sentence splits. | backend,pipeline | 90 |
| T-015 | LLM adapter (Azure OpenAI) | Provider adapter with summarize_json, schema enforcement, retries. | llm/base.py; llm/azure.py; tests/test_llm_adapter.py | pytest -k llm_adapter | Mocked client tests pass; JSON validated. | backend,llm | 90 |
| T-016 | Map prompt & JSON output | Prompt returning bullets with ts/text/quote; coverage field; strict JSON. | pipeline/map_stage.py; tests/test_map_stage.py | pytest -k map_stage | Golden tests pass; schema respected. | backend,llm,pipeline | 90 |
| T-017 | Reduce merge & final Markdown | Merge bullets chronologically; produce summary.md and summary.json. | pipeline/reduce_stage.py; tests/test_reduce_stage.py | pytest -k reduce_stage | Deterministic output; fixtures pass. | backend,pipeline | 90 |
| T-018 | Validation passes | Coverage %, overlap score, length bounds; corrective prompt path. | pipeline/validate.py; tests/test_validate.py | pytest -k validate | Low-overlap fixtures trigger corrections. | backend,pipeline,quality | 90 |
| T-019 | Caching layer (Redis) | Cache by videoId\|lang\|modelTier\|promptVer\|chunking; TTL 14 days. | pipeline/cache.py; tests/test_cache.py | pytest -k cache | Hit/miss tests pass; invalidation works. | backend,cache | 60 |
