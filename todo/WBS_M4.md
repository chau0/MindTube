# M4 — Frontend & Local history

| ID | Title | Description | Files | Commands | DoD | Labels | TimeboxMinutes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-020 | Next.js shell (tabs + run form) | Input URL, submit run, tabs scaffold (Summary/Ideas/Takeaways/Transcript). | web/src/app/page.tsx; web/src/components/Tabs.tsx | npm run dev | UI renders; submit calls /runs. | frontend,ui | 90 |
| T-021 | SSE progress UI | Stage/pct/ETA, error messages mapped to taxonomy. | web/src/components/Progress.tsx; web/src/lib/sse.ts | npm run dev | Live updates during mock run. | frontend,ui | 90 |
| T-022 | Results render | Render Markdown + JSON outputs; copy/download actions. | web/src/components/Results.tsx | npm run dev | Displays artifacts from API; buttons work. | frontend,ui | 90 |
| T-023 | Local history (IndexedDB) | Store last 20 runs (LRU), search, export/import JSON; clear history. | web/src/lib/history.ts; web/src/components/HistoryPanel.tsx | npm run dev; npm run test | Cypress test adds 25 → latest 20 remain; export/import OK. | frontend,storage | 90 |
| T-024 | Accessibility & i18n basics | Keyboard nav, ARIA, EN/JA UI switch (content passthrough). | web/src/i18n/*; web/src/components/* | npm run dev | Keyboard-only usable; language toggles. | frontend,a11y,i18n | 90 |
