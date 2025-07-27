# TRANSCRIPT POLICY

**Allowed sources (in order):**
1) Client-side extraction via browser (user context).  
2) User-uploaded SRT/VTT files.  
3) Unofficial transcript library — **feature-flagged OFF by default**.  
4) ASR (Whisper) — **opt-in**, 120-minute hard limit.

**Not allowed:** Scraping protected/member/age-restricted content; automated login flows.

**UI messaging:**
- Quick transcript (may be incomplete) — toggle with disclaimer.
- Offer upload if quick transcript fails.
- Offer ASR with estimated cost/time if no text available.
