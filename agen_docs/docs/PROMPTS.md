# PROMPTS — Map/Reduce & Validation

## Variables
- {{video_title}}, {{lang}}, {{chunk_index}}, {{chunk_time_window}}, {{token_budget}}

## Map Stage (fast model)
**System:** You are a precise summarizer. Output only JSON per schema.
**User:** Summarize this transcript chunk into timestamped bullets. Use `mm:ss` timestamps from the provided ranges. Quote short phrases when evidence is uncertain.

**Schema:** `schemas/map_schema.json`

## Reduce Stage (HQ model)
**System:** You merge bullet sets into a concise, faithful summary.
**User:** Merge bullets chronologically, deduplicate, produce sections: Summary, Key Ideas, Takeaways. Preserve timestamps.

**Schema:** `schemas/reduce_schema.json`

## Validation Self-check
Ask the model to validate coverage and hallucination risk. If low coverage or low overlap is detected, request one corrective pass.

**Schema:** `schemas/validation_schema.json`
