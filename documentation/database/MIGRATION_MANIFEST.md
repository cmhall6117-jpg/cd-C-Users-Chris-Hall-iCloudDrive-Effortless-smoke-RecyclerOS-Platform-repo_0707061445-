# Migration Manifest

## PostgreSQL Order

- 001_initial_schema.sql
- 002_opportunity_discovery.sql
- 003_vehicle_digital_twin.sql
- 004_procurement_workspace.sql
- 005_pick_list_focus_point.sql
- 006_inventory_intake.sql
- 022_integration_readiness.sql
- 023_local_integration_bundle.sql
- 024_rc1_tenant_scope.sql
- 025_rc1_database_consolidation.sql

## SQLite Order

- 001_initial_offline_schema.sql
- 002_opportunity_discovery.sql
- 003_vehicle_digital_twin.sql
- 004_procurement_workspace.sql
- 005_pick_list_focus_point.sql
- 006_inventory_intake.sql
- 022_integration_readiness.sql
- 023_local_integration_bundle.sql
- 024_rc1_tenant_scope.sql
- 025_rc1_database_consolidation.sql

## Normalization Findings

- No duplicate migration numbers were found in the active PostgreSQL set.
- No duplicate migration numbers were found in the active SQLite set.
- Number gaps exist between `006` and `022`; these gaps are intentionally preserved because intermediate generated slices were not merged into the active RC1 path.
- `024_rc1_tenant_scope.sql` was added instead of rewriting generated migrations.
- `025_rc1_database_consolidation.sql` consolidates tenant seed data, sync queue parity, tenant indexes, and database-level tenant/workspace enforcement.

## Tenant Scope

The RC1 normalization migration adds `organization_id` and `workspace_id` to tenant-owned records used by the active path:

- vehicles
- opportunities
- business_events
- vehicle_timeline
- procurement_analyses
- procurement_scenarios
- pick_list_items
- harvest_sessions
- harvested_parts
- storage_locations
- inventory_items
- integration_smoke_test_runs
- integration_issues

## SQLite Result

SQLite clean initialization passed locally on July 13, 2026. Evidence is in `build_artifacts/sqlite_init_report.txt`.

SQLite clean initialization with consolidation migration passed locally on July 14, 2026. The check now also verifies tenant columns on tenant-owned tables and confirms invalid tenant/workspace inserts are rejected.

GitHub Actions repeated the clean SQLite initialization successfully on core
working path PR run `29325554779`.

## PostgreSQL Result

PostgreSQL local execution is blocked in this environment because Docker is not
installed or not available on PATH. GitHub Actions PR run `29325554779` applied
all ten active migrations successfully against a clean PostgreSQL 16 service by
using `tools/scripts/rc1_postgres_migrate.py`.

The PostgreSQL consolidation migration creates the missing PostgreSQL `sync_queue` table for parity with SQLite and adds tenant validation triggers for tenant-owned records.
