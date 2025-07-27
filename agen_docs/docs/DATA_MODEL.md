# DATA MODEL — MindTube (MVP)

## Tables
### videos
- id (uuid, pk)
- youtube_id (text, idx)
- title (text)
- duration_sec (int)
- lang (text)
- created_at (timestamptz default now())

### runs
- id (uuid, pk)
- video_id (uuid, fk videos.id)
- status (text: QUEUED|RUNNING|SUCCEEDED|FAILED|CANCELED, idx)
- started_at (timestamptz)
- finished_at (timestamptz, null)
- model_map (text)
- model_reduce (text)
- prompt_version (text)
- params_json (jsonb)
- error_code (text, null)
- cost_cents (int, default 0)

### artifacts
- id (uuid, pk)
- run_id (uuid, fk runs.id, idx)
- kind (text enum: captions|transcript|chunks|map_partials|summary_md|summary_json)
- path (text)
- bytes (int)
- sha256 (text)
- created_at (timestamptz default now())

### metrics
- id (uuid, pk)
- run_id (uuid, fk runs.id, idx)
- stage (text)
- ms (int)
- token_input (int)
- token_output (int)
- model (text)
- created_at (timestamptz default now())
