INSERT OR IGNORE INTO organizations (id, name, created_at)
VALUES ('org-local', 'Local Organization', datetime('now'));

INSERT OR IGNORE INTO workspaces (id, organization_id, name, created_at)
VALUES ('workspace-local', 'org-local', 'Local Workspace', datetime('now'));

ALTER TABLE sync_queue ADD COLUMN organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE sync_queue ADD COLUMN workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

CREATE INDEX IF NOT EXISTS idx_business_events_tenant ON business_events(organization_id, workspace_id);
CREATE INDEX IF NOT EXISTS idx_vehicle_timeline_tenant ON vehicle_timeline(organization_id, workspace_id);
CREATE INDEX IF NOT EXISTS idx_procurement_analyses_tenant ON procurement_analyses(organization_id, workspace_id);
CREATE INDEX IF NOT EXISTS idx_procurement_scenarios_tenant ON procurement_scenarios(organization_id, workspace_id);
CREATE INDEX IF NOT EXISTS idx_pick_list_items_tenant ON pick_list_items(organization_id, workspace_id);
CREATE INDEX IF NOT EXISTS idx_harvest_sessions_tenant ON harvest_sessions(organization_id, workspace_id);
CREATE INDEX IF NOT EXISTS idx_harvested_parts_tenant ON harvested_parts(organization_id, workspace_id);
CREATE INDEX IF NOT EXISTS idx_storage_locations_tenant ON storage_locations(organization_id, workspace_id);
CREATE INDEX IF NOT EXISTS idx_integration_smoke_test_runs_tenant ON integration_smoke_test_runs(organization_id, workspace_id);
CREATE INDEX IF NOT EXISTS idx_integration_issues_tenant ON integration_issues(organization_id, workspace_id);
CREATE INDEX IF NOT EXISTS idx_sync_queue_tenant ON sync_queue(organization_id, workspace_id);

CREATE TRIGGER IF NOT EXISTS trg_vehicles_rc1_tenant
BEFORE INSERT ON vehicles
FOR EACH ROW WHEN NOT EXISTS (SELECT 1 FROM workspaces WHERE id = NEW.workspace_id AND organization_id = NEW.organization_id)
BEGIN
    SELECT RAISE(ABORT, 'workspace_id does not belong to organization_id');
END;

CREATE TRIGGER IF NOT EXISTS trg_opportunities_rc1_tenant
BEFORE INSERT ON opportunities
FOR EACH ROW WHEN NOT EXISTS (SELECT 1 FROM workspaces WHERE id = NEW.workspace_id AND organization_id = NEW.organization_id)
BEGIN
    SELECT RAISE(ABORT, 'workspace_id does not belong to organization_id');
END;

CREATE TRIGGER IF NOT EXISTS trg_business_events_rc1_tenant
BEFORE INSERT ON business_events
FOR EACH ROW WHEN NOT EXISTS (SELECT 1 FROM workspaces WHERE id = NEW.workspace_id AND organization_id = NEW.organization_id)
BEGIN
    SELECT RAISE(ABORT, 'workspace_id does not belong to organization_id');
END;

CREATE TRIGGER IF NOT EXISTS trg_sync_queue_rc1_tenant
BEFORE INSERT ON sync_queue
FOR EACH ROW WHEN NOT EXISTS (SELECT 1 FROM workspaces WHERE id = NEW.workspace_id AND organization_id = NEW.organization_id)
BEGIN
    SELECT RAISE(ABORT, 'workspace_id does not belong to organization_id');
END;

CREATE TRIGGER IF NOT EXISTS trg_vehicle_timeline_rc1_tenant
BEFORE INSERT ON vehicle_timeline
FOR EACH ROW WHEN NOT EXISTS (SELECT 1 FROM workspaces WHERE id = NEW.workspace_id AND organization_id = NEW.organization_id)
BEGIN
    SELECT RAISE(ABORT, 'workspace_id does not belong to organization_id');
END;

CREATE TRIGGER IF NOT EXISTS trg_procurement_analyses_rc1_tenant
BEFORE INSERT ON procurement_analyses
FOR EACH ROW WHEN NOT EXISTS (SELECT 1 FROM workspaces WHERE id = NEW.workspace_id AND organization_id = NEW.organization_id)
BEGIN
    SELECT RAISE(ABORT, 'workspace_id does not belong to organization_id');
END;

CREATE TRIGGER IF NOT EXISTS trg_procurement_scenarios_rc1_tenant
BEFORE INSERT ON procurement_scenarios
FOR EACH ROW WHEN NOT EXISTS (SELECT 1 FROM workspaces WHERE id = NEW.workspace_id AND organization_id = NEW.organization_id)
BEGIN
    SELECT RAISE(ABORT, 'workspace_id does not belong to organization_id');
END;

CREATE TRIGGER IF NOT EXISTS trg_pick_list_items_rc1_tenant
BEFORE INSERT ON pick_list_items
FOR EACH ROW WHEN NOT EXISTS (SELECT 1 FROM workspaces WHERE id = NEW.workspace_id AND organization_id = NEW.organization_id)
BEGIN
    SELECT RAISE(ABORT, 'workspace_id does not belong to organization_id');
END;

CREATE TRIGGER IF NOT EXISTS trg_harvest_sessions_rc1_tenant
BEFORE INSERT ON harvest_sessions
FOR EACH ROW WHEN NOT EXISTS (SELECT 1 FROM workspaces WHERE id = NEW.workspace_id AND organization_id = NEW.organization_id)
BEGIN
    SELECT RAISE(ABORT, 'workspace_id does not belong to organization_id');
END;

CREATE TRIGGER IF NOT EXISTS trg_harvested_parts_rc1_tenant
BEFORE INSERT ON harvested_parts
FOR EACH ROW WHEN NOT EXISTS (SELECT 1 FROM workspaces WHERE id = NEW.workspace_id AND organization_id = NEW.organization_id)
BEGIN
    SELECT RAISE(ABORT, 'workspace_id does not belong to organization_id');
END;

CREATE TRIGGER IF NOT EXISTS trg_storage_locations_rc1_tenant
BEFORE INSERT ON storage_locations
FOR EACH ROW WHEN NOT EXISTS (SELECT 1 FROM workspaces WHERE id = NEW.workspace_id AND organization_id = NEW.organization_id)
BEGIN
    SELECT RAISE(ABORT, 'workspace_id does not belong to organization_id');
END;

CREATE TRIGGER IF NOT EXISTS trg_inventory_items_rc1_tenant
BEFORE INSERT ON inventory_items
FOR EACH ROW WHEN NOT EXISTS (SELECT 1 FROM workspaces WHERE id = NEW.workspace_id AND organization_id = NEW.organization_id)
BEGIN
    SELECT RAISE(ABORT, 'workspace_id does not belong to organization_id');
END;

CREATE TRIGGER IF NOT EXISTS trg_integration_smoke_test_runs_rc1_tenant
BEFORE INSERT ON integration_smoke_test_runs
FOR EACH ROW WHEN NOT EXISTS (SELECT 1 FROM workspaces WHERE id = NEW.workspace_id AND organization_id = NEW.organization_id)
BEGIN
    SELECT RAISE(ABORT, 'workspace_id does not belong to organization_id');
END;

CREATE TRIGGER IF NOT EXISTS trg_integration_issues_rc1_tenant
BEFORE INSERT ON integration_issues
FOR EACH ROW WHEN NOT EXISTS (SELECT 1 FROM workspaces WHERE id = NEW.workspace_id AND organization_id = NEW.organization_id)
BEGIN
    SELECT RAISE(ABORT, 'workspace_id does not belong to organization_id');
END;
