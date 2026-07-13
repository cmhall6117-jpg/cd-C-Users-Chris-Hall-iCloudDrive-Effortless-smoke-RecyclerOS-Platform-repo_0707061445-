CREATE TABLE IF NOT EXISTS integration_smoke_test_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_code TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,
    summary TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
