INSERT INTO organizations (id, name)
VALUES ('org-local', 'Local Organization')
ON CONFLICT (id) DO NOTHING;

INSERT INTO workspaces (id, organization_id, name)
VALUES ('workspace-local', 'org-local', 'Local Workspace')
ON CONFLICT (id) DO NOTHING;

CREATE TABLE IF NOT EXISTS sync_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID REFERENCES business_events(id),
    action TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'pending',
    retry_count INTEGER NOT NULL DEFAULT 0
);

ALTER TABLE sync_queue ADD COLUMN IF NOT EXISTS organization_id TEXT NOT NULL DEFAULT 'org-local';
ALTER TABLE sync_queue ADD COLUMN IF NOT EXISTS workspace_id TEXT NOT NULL DEFAULT 'workspace-local';

CREATE UNIQUE INDEX IF NOT EXISTS idx_workspaces_id_org ON workspaces(id, organization_id);

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

CREATE OR REPLACE FUNCTION ensure_rc1_workspace_tenant()
RETURNS trigger AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM workspaces
        WHERE id = NEW.workspace_id
          AND organization_id = NEW.organization_id
    ) THEN
        RAISE EXCEPTION 'workspace_id % does not belong to organization_id %', NEW.workspace_id, NEW.organization_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
DECLARE
    tenant_table TEXT;
BEGIN
    FOREACH tenant_table IN ARRAY ARRAY[
        'vehicles',
        'opportunities',
        'business_events',
        'sync_queue',
        'vehicle_timeline',
        'procurement_analyses',
        'procurement_scenarios',
        'pick_list_items',
        'harvest_sessions',
        'harvested_parts',
        'storage_locations',
        'inventory_items',
        'integration_smoke_test_runs',
        'integration_issues'
    ]
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS trg_%I_rc1_tenant ON %I', tenant_table, tenant_table);
        EXECUTE format(
            'CREATE TRIGGER trg_%I_rc1_tenant BEFORE INSERT OR UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION ensure_rc1_workspace_tenant()',
            tenant_table,
            tenant_table
        );
    END LOOP;
END $$;
