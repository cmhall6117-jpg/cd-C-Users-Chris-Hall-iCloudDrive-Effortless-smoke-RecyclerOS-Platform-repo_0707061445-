# Smoke Test Report

## Local Smoke Checks

### SQLite Migration Initialization

Result: passed

Evidence:

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
```

### Backend Tenant Isolation

Result: passed in CI

Evidence: GitHub Actions `backend` job succeeded on run `29289307269`.

Tests added:

- missing tenant context rejected for opportunities
- matching tenant context accepted for opportunity creation
- mismatched organization rejected
- vehicle record requires tenant context
- mismatched inventory workspace rejected

### Flutter Primary Path

Result: passed in CI

Evidence: GitHub Actions `flutter` job succeeded on run `29289307269`.

Routes added:

- `/`
- `/workspace-select`
- `/mission-control`
- `/opportunities`
- `/vehicles/:vehicleCode`
- `/procurement/:opportunityId`
- `/pick-list`
- `/focus-point/:vehicleId`
- `/inventory/intake`
