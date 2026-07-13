CREATE TABLE IF NOT EXISTS organizations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workspaces (
    id TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

ALTER TABLE vehicles ADD COLUMN organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE vehicles ADD COLUMN workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE opportunities ADD COLUMN organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE opportunities ADD COLUMN workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE business_events ADD COLUMN organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE business_events ADD COLUMN workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE vehicle_timeline ADD COLUMN organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE vehicle_timeline ADD COLUMN workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE procurement_analyses ADD COLUMN organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE procurement_analyses ADD COLUMN workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE procurement_scenarios ADD COLUMN organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE procurement_scenarios ADD COLUMN workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE pick_list_items ADD COLUMN organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE pick_list_items ADD COLUMN workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE harvest_sessions ADD COLUMN organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE harvest_sessions ADD COLUMN workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE harvested_parts ADD COLUMN organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE harvested_parts ADD COLUMN workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE storage_locations ADD COLUMN organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE storage_locations ADD COLUMN workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE inventory_items ADD COLUMN organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE inventory_items ADD COLUMN workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE integration_smoke_test_runs ADD COLUMN organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE integration_smoke_test_runs ADD COLUMN workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

ALTER TABLE integration_issues ADD COLUMN organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE integration_issues ADD COLUMN workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

CREATE INDEX IF NOT EXISTS idx_vehicles_tenant ON vehicles(organization_id, workspace_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_tenant ON opportunities(organization_id, workspace_id);
CREATE INDEX IF NOT EXISTS idx_inventory_items_tenant ON inventory_items(organization_id, workspace_id);
