-- MindTube DDL (SQLite syntax; adapt for Postgres)
CREATE TABLE IF NOT EXISTS videos (
  id TEXT PRIMARY KEY,
  youtube_id TEXT NOT NULL,
  title TEXT,
  duration_sec INTEGER,
  lang TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_videos_youtube_id ON videos(youtube_id);

CREATE TABLE IF NOT EXISTS runs (
  id TEXT PRIMARY KEY,
  video_id TEXT REFERENCES videos(id),
  status TEXT NOT NULL,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  model_map TEXT,
  model_reduce TEXT,
  prompt_version TEXT,
  params_json TEXT,
  error_code TEXT,
  cost_cents INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_runs_status_started ON runs(status, started_at DESC);

CREATE TABLE IF NOT EXISTS artifacts (
  id TEXT PRIMARY KEY,
  run_id TEXT REFERENCES runs(id),
  kind TEXT NOT NULL,
  path TEXT NOT NULL,
  bytes INTEGER,
  sha256 TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_artifacts_run_kind ON artifacts(run_id, kind);

CREATE TABLE IF NOT EXISTS metrics (
  id TEXT PRIMARY KEY,
  run_id TEXT REFERENCES runs(id),
  stage TEXT,
  ms INTEGER,
  token_input INTEGER,
  token_output INTEGER,
  model TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
