CREATE TABLE IF NOT EXISTS storage_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    zone TEXT,
    rack TEXT,
    shelf TEXT,
    bin TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS inventory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inventory_code TEXT UNIQUE NOT NULL,
    part_name TEXT NOT NULL,
    source_vehicle_id UUID REFERENCES vehicles(id),
    harvest_session_id UUID REFERENCES harvest_sessions(id),
    storage_location_id UUID REFERENCES storage_locations(id),
    condition TEXT NOT NULL DEFAULT 'usedUntested',
    status TEXT NOT NULL DEFAULT 'available',
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity >= 0),
    estimated_value NUMERIC(12,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_inventory_items_status ON inventory_items(status);
CREATE INDEX IF NOT EXISTS idx_inventory_items_part_name ON inventory_items(part_name);
CREATE INDEX IF NOT EXISTS idx_inventory_items_vehicle ON inventory_items(source_vehicle_id);
