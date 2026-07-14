# RC1 Database Consolidation

## Purpose

This branch consolidates the RC1 database layer after the first reproducible build state. It does not create new vertical slices. It tightens the active RC1 path database model so PostgreSQL and SQLite behave more consistently.

## Changes

- Added `025_rc1_database_consolidation.sql` for PostgreSQL and SQLite.
- Seeded the default local tenant:
  - `org-local`
  - `workspace-local`
- Added PostgreSQL `sync_queue` table for parity with SQLite.
- Added `organization_id` and `workspace_id` to SQLite/PostgreSQL `sync_queue`.
- Added tenant indexes across tenant-owned tables.
- Added PostgreSQL tenant validation triggers for tenant-owned records.
- Added SQLite tenant validation triggers for tenant-owned record inserts.
- Strengthened `tools/scripts/rc1_sqlite_check.py` so it verifies:
  - all active migrations apply cleanly
  - tenant-owned tables have `organization_id` and `workspace_id`
  - mismatched tenant/workspace inserts are rejected

## Tenant-Owned Tables

- vehicles
- opportunities
- business_events
- sync_queue
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

## Local SQLite Evidence

Latest local check:

```text
PASS 001_initial_offline_schema.sql
PASS 002_opportunity_discovery.sql
PASS 003_vehicle_digital_twin.sql
PASS 004_procurement_workspace.sql
PASS 005_pick_list_focus_point.sql
PASS 006_inventory_intake.sql
PASS 022_integration_readiness.sql
PASS 023_local_integration_bundle.sql
PASS 024_rc1_tenant_scope.sql
PASS 025_rc1_database_consolidation.sql
PASS tenant columns present
PASS tenant mismatch rejected
```

## Notes

The generated migration numbering gap between `006` and `022` remains intentionally preserved. The consolidation migration is appended as `025` rather than rewriting generated package history.
