CREATE TABLE IF NOT EXISTS rc1_code_sequences (
    prefix TEXT PRIMARY KEY,
    next_value BIGINT NOT NULL CHECK (next_value > 0)
);

INSERT INTO rc1_code_sequences (prefix, next_value)
SELECT
    'OPP',
    COALESCE(
        MAX(
            CASE
                WHEN opportunity_code ~ '^OPP-[0-9]+$'
                THEN split_part(opportunity_code, '-', 2)::BIGINT
            END
        ),
        0
    ) + 1
FROM opportunities
ON CONFLICT (prefix) DO NOTHING;

INSERT INTO rc1_code_sequences (prefix, next_value)
SELECT
    'VEH',
    COALESCE(
        MAX(
            CASE
                WHEN vehicle_code ~ '^VEH-[0-9]+$'
                THEN split_part(vehicle_code, '-', 2)::BIGINT
            END
        ),
        0
    ) + 1
FROM vehicles
ON CONFLICT (prefix) DO NOTHING;

INSERT INTO rc1_code_sequences (prefix, next_value)
SELECT
    'INV',
    COALESCE(
        MAX(
            CASE
                WHEN inventory_code ~ '^INV-[0-9]+$'
                THEN split_part(inventory_code, '-', 2)::BIGINT
            END
        ),
        0
    ) + 1
FROM inventory_items
ON CONFLICT (prefix) DO NOTHING;

CREATE TABLE IF NOT EXISTS auth_users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_auth_users_email_normalized
ON auth_users (LOWER(email));

CREATE TABLE IF NOT EXISTS auth_password_credentials (
    user_id TEXT PRIMARY KEY REFERENCES auth_users(id) ON DELETE CASCADE,
    password_salt BYTEA NOT NULL,
    password_digest BYTEA NOT NULL,
    password_iterations INTEGER NOT NULL CHECK (password_iterations >= 1000),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS auth_tenant_memberships (
    user_id TEXT NOT NULL REFERENCES auth_users(id) ON DELETE CASCADE,
    organization_id TEXT NOT NULL REFERENCES organizations(id),
    workspace_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('owner', 'admin', 'operator', 'viewer')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, organization_id, workspace_id),
    FOREIGN KEY (workspace_id, organization_id)
        REFERENCES workspaces(id, organization_id)
);

CREATE INDEX IF NOT EXISTS idx_auth_memberships_tenant
ON auth_tenant_memberships (organization_id, workspace_id);

CREATE TABLE IF NOT EXISTS auth_sessions (
    token_digest TEXT PRIMARY KEY CHECK (length(token_digest) = 64),
    user_id TEXT NOT NULL REFERENCES auth_users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_auth_sessions_user
ON auth_sessions (user_id, expires_at);

CREATE INDEX IF NOT EXISTS idx_auth_sessions_active
ON auth_sessions (expires_at)
WHERE revoked_at IS NULL;

CREATE TABLE IF NOT EXISTS auth_login_attempts (
    email TEXT PRIMARY KEY,
    failure_count INTEGER NOT NULL DEFAULT 0 CHECK (failure_count >= 0),
    last_failed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    blocked_until TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS auth_audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT REFERENCES auth_users(id) ON DELETE SET NULL,
    email TEXT,
    event_type TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    details JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_auth_audit_events_user_time
ON auth_audit_events (user_id, occurred_at DESC);

CREATE INDEX IF NOT EXISTS idx_auth_audit_events_type_time
ON auth_audit_events (event_type, occurred_at DESC);
