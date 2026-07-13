CREATE TABLE IF NOT EXISTS integration_issues (
    id TEXT PRIMARY KEY,
    issue_code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'medium',
    status TEXT NOT NULL DEFAULT 'open',
    related_package TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    sync_status TEXT NOT NULL DEFAULT 'pending'
);
