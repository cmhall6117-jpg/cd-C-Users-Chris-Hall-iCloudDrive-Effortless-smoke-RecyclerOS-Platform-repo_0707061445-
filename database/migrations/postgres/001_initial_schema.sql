CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_code TEXT UNIQUE NOT NULL,
    vin TEXT UNIQUE,
    year INTEGER,
    make TEXT,
    model TEXT,
    trim TEXT,
    engine TEXT,
    drivetrain TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    source_type TEXT NOT NULL,
    procurement_intent TEXT NOT NULL DEFAULT 'undecided',
    vehicle_id UUID REFERENCES vehicles(id),
    status TEXT NOT NULL DEFAULT 'discovered',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS business_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_code TEXT UNIQUE NOT NULL,
    event_type TEXT NOT NULL,
    object_type TEXT NOT NULL,
    object_id TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb
);
