CREATE TABLE IF NOT EXISTS integration_smoke_test_runs (
    id TEXT PRIMARY KEY,
    run_code TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,
    summary TEXT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    sync_status TEXT NOT NULL DEFAULT 'pending'
);
