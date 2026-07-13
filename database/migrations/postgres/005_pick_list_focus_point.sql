CREATE TABLE IF NOT EXISTS pick_list_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID REFERENCES vehicles(id),
    yard_name TEXT NOT NULL,
    yard_row TEXT,
    availability_status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS harvest_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID REFERENCES vehicles(id),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    latitude NUMERIC(10,7),
    longitude NUMERIC(10,7),
    status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS harvested_parts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    harvest_session_id UUID REFERENCES harvest_sessions(id),
    part_name TEXT NOT NULL,
    availability_confirmed BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
