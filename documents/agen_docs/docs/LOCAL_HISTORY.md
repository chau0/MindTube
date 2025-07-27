# LOCAL HISTORY (Front-End)

- Storage: IndexedDB (`history` store)
- Fields: `runId`, `youtubeId`, `title`, `duration`, `processedAt`, `resultLinks`, `summaryPreview`
- Capacity: 20 items (LRU eviction)
- Export/Import: JSON file; schema versioned
- Privacy: Stays in browser unless user exports
- UI: History panel with search; clear history button
