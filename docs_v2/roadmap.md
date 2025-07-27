# MindTube — Roadmap (CLI → API → Frontend)
**Version:** 2025-07-27

## 0) Principles
- Local-first, minimal infra (≤ $10/mo). 
- One reusable core pipeline for CLI/API/FE.
- LLM provider abstraction (Azure first; swappable).

## 1) Phases
1. **CLI MVP**: captions → ASR fallback → chunk → map/reduce → exports (MD/JSON/Mermaid) + cache.
2. **Hardening**: error taxonomy, schemas, logging/cost, determinism, tests & docs.
3. **API (FastAPI)**: `/runs`, status, artifacts; background runner; static serve; API key; Docker.
4. **Frontend (Next.js)**: submit URL, status, tabs (Summary, Key Ideas, Takeaways, Transcript, Mindmap).
5. **Scale/Polish** (opt.): workers/queue, object storage, rate limits, observability.

## 2) Week-by-Week (suggested)
- **Week 1**: CLI core (captions, chunking, FakeLLM); exporters; E2E with fakes.
- **Week 2**: ASR fallback; cache; cost guards; docs.
- **Week 3**: API wrapper; background jobs; Docker; E2E via curl.
- **Week 4**: Frontend minimal UI; Mermaid/Markdown rendering; polish.

## 3) Deliverables
- CLI binary/script `mindtube`.
- Artifacts: `notes.md`, `summary.json`, `mindmap.mmd`, `transcript.jsonl`.
- API endpoints + container.
- Minimal FE.

## 4) Risks & Mitigations
- Captions missing → ASR cached.
- Long videos → chunking + map/reduce.
- Costs → small models, JSON mode, caching.
- Mindmap clutter → depth/breadth limits.
