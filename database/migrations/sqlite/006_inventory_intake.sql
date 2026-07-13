CREATE TABLE IF NOT EXISTS storage_locations (
    id TEXT PRIMARY KEY,
    location_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    zone TEXT,
    rack TEXT,
    shelf TEXT,
    bin TEXT,
    created_at TEXT NOT NULL,
    sync_status TEXT NOT NULL DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS inventory_items (
    id TEXT PRIMARY KEY,
    inventory_code TEXT UNIQUE NOT NULL,
    part_name TEXT NOT NULL,
    source_vehicle_id TEXT,
    harvest_session_id TEXT,
    storage_location_id TEXT,
    condition TEXT NOT NULL DEFAULT 'usedUntested',
    status TEXT NOT NULL DEFAULT 'available',
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity >= 0),
    estimated_value REAL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    sync_status TEXT NOT NULL DEFAULT 'pending'
);

CREATE INDEX IF NOT EXISTS idx_inventory_items_status ON inventory_items(status);
CREATE INDEX IF NOT EXISTS idx_inventory_items_part_name ON inventory_items(part_name);
CREATE INDEX IF NOT EXISTS idx_inventory_items_vehicle ON inventory_items(source_vehicle_id);
