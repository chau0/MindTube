# MindTube Product Requirements Document (PRD)

## 🧠 App Goal
- **Input:** YouTube URL
- **Output:** Key ideas, takeaways, mind map, transcript search, summaries, etc.

---

## ⚙️ Core Features

### 1. Transcript Extraction
- Fetch auto-generated transcript (YouTube API or youtube-transcript-api)
- Fallback: Use Whisper ASR if transcript unavailable

### 2. LLM Content Exploration
- Summaries: Short, detailed, and timestamped
- Key takeaways / insights
- Bullet-point highlights
- Mindmap (convertible to visual)
- Q&A based on video content

### 3. User Interface
- Input: Paste YouTube URL
- Output: Tabs/sections for Summary, Takeaways, Mindmap, Transcript
- Export options: Markdown, Notion, PDF, etc.

---

## 🧱 Tech Stack Suggestions

### Backend
| Area                | Tools/Tech                          |
|---------------------|-------------------------------------|
| LLM                 | OpenAI GPT-4o / Claude / Gemini     |
| Transcript Fetching | youtube-transcript-api, Whisper     |
| Mindmap Format      | mermaid, mindmap.js, or custom      |
| Summarization       | Chunk + summarize + refine/map-reduce|
| Hosting             | Render, Railway, Supabase Edge      |

### Frontend
| Area         | Tools/Tech                        |
|--------------|-----------------------------------|
| Framework    | React or Next.js                  |
| Visualization| react-flow, d3, mermaid, mindmap.js|
| UI Kit       | Tailwind + shadcn/ui or Chakra    |
| Auth (opt.)  | Clerk / Supabase / Auth0          |

---

## 🧠 Prompt Engineering

### Summarization Template
> You are an expert summarizer. Given a YouTube transcript, break it down into:
> 1. Main topic summary
> 2. Key takeaways (with timestamps if available)
> 3. Bullet points for each major idea

### Mindmap Generation Template
> Convert this video summary into a hierarchical mindmap JSON. Structure:
> - Root: Topic
>   - Main Point A
>     - Subpoint A1
>     - Subpoint A2
>   - Main Point B
> ...

---

## 🧪 Monetization Ideas
- Freemium: Free for short videos, paid for longer videos or PDF export
- Chrome Extension: Summarize YouTube in 1-click
- Notion Integration: Save outputs into structured pages
- Learning tools: Spaced repetition Q&A

---

## 🧪 MVP Roadmap (2-4 weeks)

### Week 1: Setup
- Transcript extraction
- LLM pipeline (summarization & key ideas)
- Local prototype (Streamlit / Flask + OpenAI)

### Week 2: Frontend & Output Formats
- Build React UI (paste URL, view output)
- Support Markdown export
- Basic mindmap rendering

### Week 3–4: Polish & Extras
- Visual mindmap
- Caching/DB for transcript & output reuse
- Deploy to Vercel / Render