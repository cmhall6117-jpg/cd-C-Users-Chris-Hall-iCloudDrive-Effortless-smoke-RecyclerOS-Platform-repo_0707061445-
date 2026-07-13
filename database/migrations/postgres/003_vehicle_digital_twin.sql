ALTER TABLE vehicles
ADD COLUMN IF NOT EXISTS transmission TEXT,
ADD COLUMN IF NOT EXISTS exterior_color TEXT,
ADD COLUMN IF NOT EXISTS interior_color TEXT,
ADD COLUMN IF NOT EXISTS mileage INTEGER,
ADD COLUMN IF NOT EXISTS lifecycle_status TEXT NOT NULL DEFAULT 'discovered',
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

CREATE TABLE IF NOT EXISTS vehicle_timeline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID REFERENCES vehicles(id),
    event_id UUID REFERENCES business_events(id),
    title TEXT NOT NULL,
    description TEXT,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vehicle_timeline_vehicle ON vehicle_timeline(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_lifecycle_status ON vehicles(lifecycle_status);
