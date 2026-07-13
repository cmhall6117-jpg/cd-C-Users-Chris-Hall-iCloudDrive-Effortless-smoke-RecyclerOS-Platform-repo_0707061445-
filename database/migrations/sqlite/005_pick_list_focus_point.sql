CREATE TABLE IF NOT EXISTS pick_list_items (
    id TEXT PRIMARY KEY,
    vehicle_id TEXT NOT NULL,
    yard_name TEXT NOT NULL,
    yard_row TEXT,
    availability_status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    sync_status TEXT NOT NULL DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS harvest_sessions (
    id TEXT PRIMARY KEY,
    vehicle_id TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    latitude REAL,
    longitude REAL,
    status TEXT NOT NULL DEFAULT 'active',
    sync_status TEXT NOT NULL DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS harvested_parts (
    id TEXT PRIMARY KEY,
    harvest_session_id TEXT NOT NULL,
    part_name TEXT NOT NULL,
    availability_confirmed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    sync_status TEXT NOT NULL DEFAULT 'pending'
);
