# Copilot Instructions for MindTube

## Project Overview
MindTube is an MVP-focused YouTube summarization tool. It ingests YouTube URLs, fetches metadata/captions, normalizes transcripts, and summarizes content using a map/reduce pipeline. The architecture is split into API, Backend, and Frontend components, with clear boundaries and responsibilities.

## Architecture & Data Flow
- **API**: Main endpoints are `/ingest`, `/status`, `/result`, and `/metrics`. Parameters (e.g., language, ASR, duration cap) are accepted via `/ingest`.
- **Backend**: Handles YouTube API integration, transcript normalization, chunking, orchestration, caching, concurrency control, and observability. Uses structured logging and counters for metrics.
- **Frontend**: UI is tab-based (Summary, Key Ideas, Takeaways, Transcript), with features like progress widgets, error modals, local history, transcript search, and settings modal (local storage).
- **Concurrency**: Max 3 concurrent jobs; others are queued. Cancel and queue state are exposed in `/status` and UI.
- **ASR Fallback**: Whisper-based speech-to-text is opt-in if captions are missing.

## Developer Workflows
- **Feature Table**: All MVP features, priorities, and work splits are tracked in `docs/features.md`.
- **Change Log**: Versioning and major changes are tracked at the bottom of `docs/features.md`.
- **No build/test scripts found**: If present, document in this file. Otherwise, add build/test instructions here when available.

## Conventions & Patterns
- **Feature IDs**: All features use `F-XXX` IDs for cross-referencing.
- **Error Handling**: Standardized error payloads from API; frontend displays friendly modals/banners.
- **Caching**: Idempotency via transcript hash; cache badge shown in UI if loaded from cache.
- **Local Storage**: Used for settings and history (last 20 runs).
- **Markdown Export**: UI supports copy/download of Markdown mirroring results tabs.

## Integration Points
- **YouTube API**: Used for metadata/captions fetch; quota and error mapping handled in backend.
- **Whisper ASR**: Used for speech-to-text fallback.
- **Frontend/Backend Communication**: API endpoints are the main integration points; respect documented schemas and flags.

## Key Files & Directories
- `docs/features.md`: Canonical source for features, priorities, and architecture split.
- `docs/`: Contains design docs, roadmap, PRD, test plan, and user flows.

## Example Patterns
- **Settings Modal**: Accepts language, duration cap, ASR default, budget guardrail; persists to local storage.
- **Queueing**: Backend enforces concurrency; UI shows queued state and cancel button.
- **Progress Reporting**: `/status` endpoint and frontend widget show stage progress and partial output.

---
For missing build/test/debug instructions, update this file as those scripts are added. For questions about unclear conventions, ask the PM/Builder.
