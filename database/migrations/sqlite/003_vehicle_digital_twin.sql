ALTER TABLE vehicles ADD COLUMN transmission TEXT;
ALTER TABLE vehicles ADD COLUMN exterior_color TEXT;
ALTER TABLE vehicles ADD COLUMN interior_color TEXT;
ALTER TABLE vehicles ADD COLUMN mileage INTEGER;
ALTER TABLE vehicles ADD COLUMN lifecycle_status TEXT NOT NULL DEFAULT 'discovered';
ALTER TABLE vehicles ADD COLUMN updated_at TEXT;

CREATE TABLE IF NOT EXISTS vehicle_timeline (
    id TEXT PRIMARY KEY,
    vehicle_id TEXT NOT NULL,
    event_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    occurred_at TEXT NOT NULL,
    sync_status TEXT NOT NULL DEFAULT 'pending'
);

CREATE INDEX IF NOT EXISTS idx_vehicle_timeline_vehicle ON vehicle_timeline(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_lifecycle_status ON vehicles(lifecycle_status);
