# MindTube — TDD Playbook
**Version:** 2025-07-27

## Rules
1. Start with a user story → write a failing acceptance test (AT).
2. Red → Green → Refactor. Add only code to pass tests.
3. Isolate side effects (network, file, LLM, ASR) behind interfaces.
4. Use jsonschema & snapshots for artifacts.

## Test Pyramid
- **Unit:** parsing, chunking, exporters, adapter contracts.
- **Service:** pipeline with fakes; tmp filesystem.
- **E2E (optional/marked):** real LLM/YouTube.
- **FE:** component tests + Playwright smoke.

## Tooling
`pytest`, `pytest-mock`, `jsonschema`, `syrupy` (snapshots), `hypothesis` (props), `responses`/`respx`, `freezegun`, `ruff`, `mypy`, coverage.

## Dependency Seams
- TranscriptSource, AudioFetcher, ASR, LLMClient, Clock/UUID, FS root.

## Milestones & ATs
- **M1 (CLI, captions):** AT-01 CLI smoke with fakes → artifacts exist & validate.
- **M2 (ASR fallback):** AT-03 force-asr path passes.
- **M3 (Quality):** AT-04 friendly errors & exit codes.
- **M4 (API):** AT-05 POST /runs → done; artifacts downloadable.
- **M5 (FE):** AT-06 Paste URL → results tabs render.

## Concrete Tests
- URL parse variants; seconds→mm:ss; chunk bounds/coverage.
- LLM adapter contract (JSON fields), retry on 429.
- Exporters snapshots (`notes.md`, `mindmap.mmd`).
- Cache hit/miss semantics.
- Pipeline service test with FakeLLM/FakeTranscriptSource.
- API TestClient route & runner state machine.

## Example Interfaces
```python
class LLMClient:
    def generate(self, system: str, user: str, json_mode: bool=True) -> dict: ...
    def summarize_chunk(self, chunk: dict) -> dict: ...
    def reduce_partials(self, maps: list[dict]) -> dict: ...
    def mindmap_from_outline(self, reduced: dict) -> str: ...
```

## CI Gates
- Lint + type check clean.
- Coverage ≥ 85% in core.
- Online tests (real LLM/YouTube) only on manual or nightly.
