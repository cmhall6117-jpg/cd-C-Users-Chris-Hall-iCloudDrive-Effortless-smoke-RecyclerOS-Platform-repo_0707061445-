CREATE TABLE IF NOT EXISTS organizations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS workspaces (
    id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL REFERENCES organizations(id),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE business_events ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE business_events ADD COLUMN IF NOT EXISTS workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE vehicle_timeline ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE vehicle_timeline ADD COLUMN IF NOT EXISTS workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE procurement_analyses ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE procurement_analyses ADD COLUMN IF NOT EXISTS workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE procurement_scenarios ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE procurement_scenarios ADD COLUMN IF NOT EXISTS workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE pick_list_items ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE pick_list_items ADD COLUMN IF NOT EXISTS workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE harvest_sessions ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE harvest_sessions ADD COLUMN IF NOT EXISTS workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE harvested_parts ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE harvested_parts ADD COLUMN IF NOT EXISTS workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE storage_locations ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE storage_locations ADD COLUMN IF NOT EXISTS workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE inventory_items ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE inventory_items ADD COLUMN IF NOT EXISTS workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE integration_smoke_test_runs ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE integration_smoke_test_runs ADD COLUMN IF NOT EXISTS workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE integration_issues ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE integration_issues ADD COLUMN IF NOT EXISTS workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

CREATE INDEX IF NOT EXISTS idx_vehicles_tenant ON vehicles(organization_id, workspace_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_tenant ON opportunities(organization_id, workspace_id);
CREATE INDEX IF NOT EXISTS idx_inventory_items_tenant ON inventory_items(organization_id, workspace_id);
