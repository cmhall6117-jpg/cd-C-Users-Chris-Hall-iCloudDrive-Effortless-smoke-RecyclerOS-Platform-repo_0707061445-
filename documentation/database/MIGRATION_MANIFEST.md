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
- 026_rc1_durable_runtime.sql

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
- `026_rc1_durable_runtime.sql` adds durable workflow code sequences and PostgreSQL auth users, credentials, memberships, sessions, login attempts, and audit events.
- Migration `026` has no SQLite counterpart because server-side credentials and sessions do not belong in the offline client database.

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
installed or not available on PATH. Earlier GitHub Actions evidence applied the
first ten active migrations successfully. Push run `29366652838` and
pull-request run `29366685297` applied all eleven active migrations against
clean PostgreSQL 16 services, then passed the durable workflow/auth restart test.

The PostgreSQL consolidation migration creates the missing PostgreSQL `sync_queue` table for parity with SQLite and adds tenant validation triggers for tenant-owned records.

## Production Execution Policy

`tools/scripts/rc1_postgres_migrate.py` now accepts `DATABASE_URL_FILE`, takes a
transaction-scoped PostgreSQL advisory lock, and records each applied filename,
SHA-256 checksum, and timestamp in `recycleros_schema_migrations`. An exact
replay is skipped. A changed checksum fails the deployment instead of silently
reapplying edited migration history.

The first ledger-enabled run replays the existing idempotent migration set and
records all eleven active files. Production CI must prove both the clean run and
the subsequent all-skip replay before the gate may pass.

## Railway PostgreSQL Execution

Railway API deployment `9ccd3586-b57f-4567-937f-0a6864d0d624` applied all
eleven active migrations against PostgreSQL 16 before application startup on
August 2, 2026. Runtime logs reported `PASS` for migrations 001 through 006 and
022 through 026, including tenant scope, database consolidation, and durable
runtime. `/v1/health/ready` then reported both storage and auth ready.

The active database deployment is
`9a092ef2-5f58-4cc8-92db-03f0af74b8d5`. Its manifest pins
`ghcr.io/railwayapp-templates/postgres-ssl:16`, one `us-east4-eqdc4a` replica,
and mount path `/var/lib/postgresql/data` on a 5,000 MiB volume. No public
database domain or TCP proxy is configured.
