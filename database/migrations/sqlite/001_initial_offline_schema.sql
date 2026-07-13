CREATE TABLE IF NOT EXISTS vehicles (
    id TEXT PRIMARY KEY,
    vehicle_code TEXT UNIQUE NOT NULL,
    vin TEXT UNIQUE,
    year INTEGER,
    make TEXT,
    model TEXT,
    trim TEXT,
    engine TEXT,
    drivetrain TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS opportunities (
    id TEXT PRIMARY KEY,
    opportunity_code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    source_type TEXT NOT NULL,
    procurement_intent TEXT NOT NULL DEFAULT 'undecided',
    vehicle_id TEXT,
    status TEXT NOT NULL DEFAULT 'discovered',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS business_events (
    id TEXT PRIMARY KEY,
    event_code TEXT UNIQUE NOT NULL,
    event_type TEXT NOT NULL,
    object_type TEXT NOT NULL,
    object_id TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    payload TEXT NOT NULL DEFAULT '{}',
    sync_status TEXT NOT NULL DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS sync_queue (
    id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    action TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    retry_count INTEGER NOT NULL DEFAULT 0
);
