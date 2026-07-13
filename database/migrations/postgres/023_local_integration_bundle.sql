CREATE TABLE IF NOT EXISTS integration_issues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    issue_code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'medium',
    status TEXT NOT NULL DEFAULT 'open',
    related_package TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
