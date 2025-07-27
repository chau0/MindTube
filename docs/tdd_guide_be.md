# MindTube TDD Playbook

This playbook turns your PRD/TDD into a concrete backlog of failing tests → passing code, with sample pytest tests, fakes, and folder structure. Copy‑paste and start.

---

## 0) Tooling & Layout

### Install dependencies

```bash
uv pip install -r <(cat <<'REQ'
pytest
pytest-asyncio
pytest-cov
hypothesis
httpx
respx
fastapi[all]
pydantic
orjson
python-multipart
sqlalchemy
alembic
REQ
)
```

### Repo structure

```bash
mindtube/
  src/
    mindtube/
      __init__.py
      api.py
      domain/
        models.py          # dataclasses / pydantic models
        chunking.py        # pure logic
        normalize.py       # pure logic
        budget.py          # token math, guardrails
        cache.py
      services/
        youtube.py         # interface + impl
        asr.py             # interface + impl
        llm.py             # interface + impl
        pipeline.py        # map/reduce orchestration
        storage.py         # artifacts
        runs.py            # repo/db ops
      infra/
        db.py              # SQLAlchemy
        di.py              # dependency wiring
  tests/
    unit/
    integration/
    e2e/
    data/                  # small fixture transcripts
  alembic/
  pytest.ini
```

### pytest.ini

```ini
[pytest]
addopts = -q --maxfail=1 --disable-warnings --cov=src/mindtube --cov-report=term-missing
asyncio_mode = auto
```

---

## 1) Test Strategy

- **Unit (fast, 70–80%)**: pure functions in domain/*
  - transcript normalization, hashing, chunking, cache key, budget caps, prompt builders
  - property-based tests for chunking boundaries (Hypothesis)
- **Integration (15–25%)**: API + service boundaries with fakes/mocks
  - FastAPI endpoints via httpx.AsyncClient/TestClient
  - YouTube/ASR/LLM HTTP stubs with respx
  - DB migrations (Alembic) + repos
- **E2E (5–10%)**: ingest → status → result using in‑memory fakes for external deps
  - Proves orchestration, SSE ordering, artifact creation

**Rule:** No real network in CI. All external APIs replaced by fakes or respx mocks.

---

## 2) Foundational Contracts

Write tests first.

**Example: tests/unit/test_models_contract.py**

```python
from mindtube.domain.models import TranscriptSegment, MapOutput

def test_transcript_segment_contract():
    seg = TranscriptSegment(start_ms=5000, end_ms=12000, text="hello")
    assert seg.duration_ms == 7000

def test_map_output_contract():
    m = MapOutput(summary="...", key_ideas=["A","B"], takeaways=["T1"])
    assert m.summary and isinstance(m.key_ideas, list)
```

**Minimal models: src/mindtube/domain/models.py**

```python
from pydantic import BaseModel

class TranscriptSegment(BaseModel):
    start_ms: int
    end_ms: int
    text: str

    @property
    def duration_ms(self) -> int:
        return self.end_ms - self.start_ms

class MapOutput(BaseModel):
    summary: str
    key_ideas: list[str]
    takeaways: list[str]
```

---

## 3) Core Domain TDD

### 3.1 Transcript normalization

**Test:**

```python
from mindtube.domain.normalize import normalize_segments, transcript_hash

def test_normalize_merges_and_trims():
    raw = [
        {"start": 0.0, "dur": 1.3, "text": "  Hello  "},
        {"start": 1.3, "dur": 2.0, "text": "world"},
        {"start": 3.3, "dur": 1.0, "text": ""},  # drop empties
    ]
    segs = normalize_segments(raw, merge_gap_ms=200)
    assert len(segs) == 1
    assert segs[0].text == "Hello world"
    assert segs[0].start_ms == 0 and segs[0].end_ms == 3300

def test_transcript_hash_is_stable():
    a = [{"start":0.0, "dur":1.0, "text":"A"}]
    b = [{"start":0.0, "dur":1.0, "text":"A"}]
    assert transcript_hash(a) == transcript_hash(b)
```

**Minimal code:**

```python
import hashlib, json
from typing import Iterable
from .models import TranscriptSegment

def normalize_segments(raw: Iterable[dict], merge_gap_ms: int = 200) -> list[TranscriptSegment]:
    # minimal: trim, drop empties, ms ints
    segs = []
    for r in raw:
        text = (r.get("text") or "").strip()
        if not text:
            continue
        start_ms = int(round(float(r["start"]) * 1000))
        end_ms = start_ms + int(round(float(r["dur"]) * 1000))
        segs.append(TranscriptSegment(start_ms=start_ms, end_ms=end_ms, text=text))

    # merge adjacent short gaps
    merged = []
    for s in segs:
        if merged and s.start_ms - merged[-1].end_ms <= merge_gap_ms:
            last = merged[-1]
            merged[-1] = TranscriptSegment(
                start_ms=last.start_ms,
                end_ms=s.end_ms,
                text=(last.text + " " + s.text).strip()
            )
        else:
            merged.append(s)
    return merged

def transcript_hash(raw: Iterable[dict]) -> str:
    # hash normalized canonical json
    norm = normalize_segments(raw, merge_gap_ms=200)
    payload = [{"s": s.start_ms, "e": s.end_ms, "t": s.text} for s in norm]
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
```

### 3.2 Chunking (property‑based)

**Test:**

```python
from hypothesis import given, strategies as st
from mindtube.domain.chunking import chunk_segments

@given(st.lists(st.tuples(st.integers(min_value=0, max_value=10_000),
                          st.integers(min_value=1, max_value=10_000),
                          st.text(min_size=1, max_size=50)), min_size=1, max_size=30))
def test_chunking_never_drops_text(cases):
    # cases as (start_ms, dur_ms, text)
    segs = [{"start": s/1000, "dur": d/1000, "text": t} for s,d,t in cases]
    chunks = chunk_segments(segs, target_tokens=2000, overlap_tokens=150)
    all_text = "".join(c["text"] for c in chunks)
    # simplify: each segment text must appear in concatenated chunk text
    for _,_,t in cases:
        assert t.strip() == "" or t in all_text

def test_chunking_respects_overlap():
    segs = [{"start":0.0, "dur":1.0, "text":"A " * 500}]
    chunks = chunk_segments(segs, target_tokens=200, overlap_tokens=50)
    assert len(chunks) > 1
    for i in range(1, len(chunks)):
        # simple heuristic: overlap exists
        assert len(set(chunks[i-1]["text"].split()) & set(chunks[i]["text"].split())) > 0
```

**Minimal code:**

```python
# src/mindtube/domain/chunking.py
from typing import Iterable
from .models import TranscriptSegment

def chunk_segments(segments: Iterable[dict], target_tokens: int, overlap_tokens: int) -> list[dict]:
    # ...existing code...
```

### 3.3 Budget guardrails

**Test:**

```python
from mindtube.domain.budget import plan_map_reduce

def test_budget_degrades_when_over_cap():
    plan = plan_map_reduce(duration_s=3600, tokens_per_second=5, map_tokens=800, reduce_tokens=2000, hard_cap=50_000)
    assert plan["degrade"] is True
    assert plan["reduce_model"] == "mini"
```

**Minimal code:**

```python
# src/mindtube/domain/budget.py
def plan_map_reduce(duration_s: int, tokens_per_second: int, map_tokens: int, reduce_tokens: int, hard_cap: int):
    # ...existing code...
```

### 3.4 Cache key

**Test:**

```python
from mindtube.domain.cache import cache_key

def test_cache_key_depends_on_video_transcript_and_params():
    k1 = cache_key("vid", "hash1", {"model":"mini","lang":"en"})
    k2 = cache_key("vid", "hash1", {"lang":"en","model":"mini"})  # order-insensitive
    assert k1 == k2
```

**Minimal code:**

```python
# src/mindtube/domain/cache.py
import hashlib
import json

def cache_key(video_id: str, transcript_hash: str, params: dict) -> str:
    # ...existing code...
```

---

## 4) Service Boundaries with Fakes (Integration TDD)

### 4.1 YouTube captions client

**Test:**

```python
import respx, httpx, pytest
from mindtube.services.youtube import YouTubeClient

@pytest.mark.asyncio
@respx.mock
async def test_fetch_captions_when_available():
    video_id = "abc123"
    # mock HTTP response to YouTube
    respx.get(...).mock(return_value=httpx.Response(200, json={"captions":[{"start":0.0,"dur":1.0,"text":"Hi"}]}))
    yt = YouTubeClient(api_key="x")
    segs = await yt.fetch_captions(video_id)
    assert segs and segs[0].text == "Hi"
```

**Minimal code:**

```python
# src/mindtube/services/youtube.py
import httpx

class YouTubeClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def fetch_captions(self, video_id: str):
        # ...existing code...
```

### 4.2 LLM client (map/reduce)

**Test:**

```python
from mindtube.services.llm import LLMClient

async def test_map_returns_expected_schema(llm_fake: LLMClient):
    out = await llm_fake.map_chunk("text")
    assert set(out.model_dump().keys()) == {"summary","key_ideas","takeaways"}
```

**Minimal code:**

```python
# src/mindtube/services/llm.py
from mindtube.domain.models import MapOutput

class LLMClient:
    async def map_chunk(self, text: str):
        return MapOutput(summary=text[:50], key_ideas=["K1","K2"], takeaways=["T1"])
```

---

## 5) Pipeline Orchestration TDD

**Test:**

```python
import asyncio
from mindtube.services.pipeline import Pipeline
from tests.fakes import FakeLLM, FakeStorage, fake_segments

async def test_pipeline_happy_path(tmp_path):
    p = Pipeline(llm=FakeLLM(), storage=FakeStorage(tmp_path))
    result = await p.run(segments=fake_segments(120), params={"reduce":"std"})
    assert "short" in result.sections
    assert result.artifacts["markdown"].endswith(".md")
```

**Minimal code:**

```python
# src/mindtube/services/pipeline.py
class Pipeline:
    def __init__(self, llm, storage):
        self.llm = llm
        self.storage = storage

    async def run(self, segments, params):
        # ...existing code...
```

---

## 6) API Surface TDD (FastAPI)

### 6.1 /ingest enqueues and returns job_id

**Test:**

```python
import pytest
from httpx import AsyncClient
from mindtube.api import build_app

@pytest.mark.asyncio
async def test_ingest_returns_job_id(monkeypatch):
    app = build_app(overrides={"queue.enqueue": lambda *a, **k: "job-1"})
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/ingest", json={"url":"https://youtube.com/watch?v=abc"})
    assert r.status_code == 200
    assert "job_id" in r.json()
```

**Minimal code:**

```python
# src/mindtube/api.py
from fastapi import FastAPI

def build_app(overrides=None):
    app = FastAPI()
    # ...existing code...
    return app
```

### 6.2 /status/{job_id} progress, /result/{job_id} payload

**Test:**

```python
@pytest.mark.asyncio
async def test_status_transitions_and_result(monkeypatch):
    app = build_app(...)
    # preload a fake run/job into repo
    # drive a fake worker to update status to done and attach artifacts
    ...
    # assert status becomes 'done' and result contains sections/links
```

**Minimal code:**

```python
# src/mindtube/api.py
@app.get("/status/{job_id}")
async def get_status(job_id: str):
    # ...existing code...
```

### 6.3 SSE stream (optional)

**Test:**

```python
# ...existing code...
```

---

## 7) E2E with All Fakes

**Test:**

```python
import pytest
from httpx import AsyncClient
from mindtube.api import build_app
from tests.fakes import FakeLLM, FakeYouTube, FakeStorage

@pytest.mark.asyncio
async def test_full_flow():
    app = build_app(overrides={
        "deps.youtube": FakeYouTube(), 
        "deps.llm": FakeLLM(),
        "deps.storage": FakeStorage()
    })
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/ingest", json={"url":"https://youtu.be/abc"})
        job_id = r.json()["job_id"]
        # simulate worker execution
        await app.state.worker.drain_once()
        st = await ac.get(f"/status/{job_id}")
        assert st.json()["status"] == "done"
        res = await ac.get(f"/result/{job_id}")
        body = res.json()
        assert "sections" in body and "links" in body
```

---

## 8) Edge Cases & Negative Tests

- No captions and ASR disabled → /ingest returns 422 with actionable message.
- YouTube rate limit → retry & backoff; status becomes error with reason.
- Token budget exceeded → degrade path chosen; tests assert reduce uses mini model.
- Cache hit → second /ingest resolves immediately with previous artifacts (test duration << fresh run).
- Very long transcripts → chunking never loses text; max overlap satisfied.
- Invalid URL or unsupported domain → 400.

---

## 9) Golden Set & Snapshots (regression)

Keep 10–15 tiny transcripts in `tests/data/`. Use snapshot testing for structured outputs.

**Example:**

```python
from pathlib import Path
from pytest_regressions.file_regression import FileRegressionFixture

def test_reduce_snapshot(file_regression: FileRegressionFixture, pipeline_with_fakes):
    segs = load_fixture_segments("short_ai_intro.json")
    result = pipeline_with_fakes.reduce(segs)
    file_regression.check(result.sections["detailed"], extension=".md")
```

---

## 10) CI & Pre‑commit

### Pre‑commit (optional)

```bash
uv pip install pre-commit ruff
pre-commit init-templated
# add hooks: ruff, black, trailing-whitespace, end-of-file-fixer
```

### CI (GitHub Actions)

```yaml
name: test
on: [push, pull_request]
jobs:
  py:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - run: uv pip install -r requirements.txt
      - run: pytest
```

---

## 11) Suggested TDD Backlog (execution order)

- Domain
  - models contract
  - normalize → hash
  - chunking (incl. property tests)
  - budget guardrails
  - cache key
- Services (fakes first)
  - FakeLLM, FakeYouTube, FakeStorage
  - Pipeline with fakes (map → reduce → artifacts)
- API
  - /ingest returns job_id, enqueues fake worker
  - /status/{id} transitions
  - /result/{id} structure & links
- Edge cases
  - ASR opt‑in required path
  - Cache hits
  - Budget degrade
- (Optional) SSE
  - event order & partials

Keep each test tiny. Commit by cycle: Red → Green → Refactor.

---

## 12) Example Fakes & Fixtures

**tests/fakes.py**

```python
from dataclasses import dataclass
from pathlib import Path
from mindtube.domain.models import MapOutput

def fake_segments(n: int):
    ms = 0
    segs = []
    for i in range(n):
        segs.append({"start": ms/1000, "dur": 2000/1000, "text": f"Sentence {i} about AI."})
        ms += 2000
    return segs

@dataclass
class FakeLLM:
    def map_chunk(self, text: str):
        return MapOutput(summary=text[:50], key_ideas=["K1","K2"], takeaways=["T1"])
    async def amap_chunk(self, text: str):  # if async needed
        return self.map_chunk(text)
    async def reduce(self, mapped: list[MapOutput]):
        return {
            "short": "Short summary.",
            "detailed": ["Point A", "Point B"],
            "ideas": [["00:00","Idea"]],
            "takeaways": ["T1","T2"]
        }

@dataclass
class FakeStorage:
    root: Path | None = None
    def __call__(self, root=None): self.root = root; return self
    async def write_markdown(self, name: str, content: str) -> str:
        p = (self.root or Path(".")) / f"{name}.md"
        p.write_text(content, encoding="utf-8")
        return str(p)
```

---

## 13) Practical Tips

- Design for injection: all services accept their clients via constructor so tests can pass fakes.
- No randomness in tests; if you need it, fix the seed.
- Keep units pure: no I/O in domain/*.
- Guard rails: add `--cov-fail-under=80` once green.
- Refactor only when green; move code between modules safely under tests.