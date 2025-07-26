# MindTube — Product Requirements Document (PRD) v1.2

**Version:** v1.2  
**Date:** 2025‑07‑26 (JST)  
**Owner:** You (PM/Builder)  
**Status:** MVP Scope Locked

---

## 1. Problem & Users

**Problem:**  
YouTube learning content is long; learners need a fast way to gauge value, extract ideas, and keep actionable notes.

**Users:**  
Self‑directed learners consuming educational, interview, or explainer videos who prefer concise summaries, timestamped highlights, and quick note export.

---

## 2. Goals & Non‑Goals

**Goals (MVP):**  
Given a YouTube URL, produce:
- Short & detailed summaries
- Bullet key ideas
- Actionable takeaways
- Downloadable transcript (if available), all optionally timestamped

**Non‑Goals (MVP):**
- Full Q&A chat
- Diagram rendering
- Notion sync
- Multi‑video batch operations
- Team sharing

---

## 3. Functional Requirements (MVP)

**Input:**  
- One YouTube URL (public/unlisted).  
- Private members‑only videos not supported.

**Transcript:**  
- Primary: Fetch captions via official API or allowed endpoints  
- Fallback: Optional ASR (e.g., Whisper) if no captions; toggle in settings  
- Keep original timestamps at sentence/segment level (≈ 5–15s granularity)

**Summarization Pipeline:**  
- Chunk transcript (~1–3k tokens/chunk), hierarchical summarize (chunk → section → whole)
- Generate:
  - 8–12 line short summary
  - 3–7 paragraph detailed summary
  - 6–12 key ideas
  - 5–10 actionable takeaways
- Include timestamped bullets (where feasible) linking to `youtube.com/watch?v=...&t=Ss`

**UI:**  
- Single page: URL input → progress steps (“Fetching transcript → Chunking → Summarizing → Finalizing”)
- Tabs or cards: Summary / Key Ideas / Takeaways / Transcript
- Controls: “Copy”, “Download .md”, “Open at timestamp”

**Export:**  
- Markdown (`.md`).  
- Filename: `<video-title>_MindTube.md`

**History:**  
- Local history list (last 20 videos) with title, channel, duration, processed at, open/delete  
- Server‑side optional

**Constraints:**  
- Max video duration (MVP): ≤ 90 minutes  
- Language: English or Japanese (others best‑effort)
- Rate limiting: 3 concurrent jobs max; queue overflow returns friendly message
- Filesize/time limits for ASR: configurable, default hard stop at 120 minutes

---

## 4. Post‑MVP (Backlog)

- Mind map generator (JSON/Graph structure, render as SVG)
- Q&A (RAG over transcript + embeddings)
- Notion/PDF export
- Multi‑language translation of summaries
- Blog post generator from video
- Server‑side user library & tags

---

## 5. Success Metrics (MVP)

- **Latency:** ≤ 15s to first short summary for a ≤10 min video with existing captions; ≤ 60s full output for ≤30 min videos
- **Completion rate:** ≥ 95% jobs complete without manual retry
- **Quality (human eval rubric):** ≥ 4/5 average on coverage, correctness, actionability for top 10 test videos
- **Usage:** ≥ 10 successful runs/day (personal target)
- **Cost:** target ≤ ¥2–¥10 per 10‑min video using “mini” models and caching (tunable)

---

## 6. Quality & Acceptance Criteria

- Input a valid URL to a video with captions → outputs all three sections with at least 80% of major topics captured (by evaluator checklist)
- Timestamped bullets jump to the correct segment (±5s)
- Markdown export matches on‑screen content, UTF‑8, ≤ 120 chars per line for bullets
- Error cases show clear guidance:
  - No transcript available → suggest ASR toggle
  - Video too long → show limit and allow override (if enabled)
  - Rate limit → show ETA and queue position (approximate)
- Privacy setting “Local‑only” stores no server data (if using desktop/PWA mode)

---

## 7. Compliance, Privacy, Legal

- Prefer official YouTube APIs and respect ToS. Avoid disallowed scraping and downloading audiovisual content.
- If using third‑party transcript libraries, verify ToS; allow user‑provided API keys.
- Privacy: no retention of transcripts by default; opt‑in for history/cloud sync.
- Clearly disclose model provider(s) and data handling.