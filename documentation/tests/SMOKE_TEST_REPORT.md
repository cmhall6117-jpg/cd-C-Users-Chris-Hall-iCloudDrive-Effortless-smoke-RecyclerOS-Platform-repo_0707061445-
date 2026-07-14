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
PASS 025_rc1_database_consolidation.sql
PASS tenant columns present
PASS tenant mismatch rejected
```

### Backend Authentication, RBAC, and Tenant Isolation

Result: passed locally and in defect-closure CI

Evidence:

- Local backend suite: 28 passed and 1 PostgreSQL-only test skipped in 13.59 seconds on the current local run.
- Pull-request run `29363414967` passed the backend job at commit
  `9bf4490f91b914b05963208355218a863b632977`.

Tests added:

- valid credentials return an opaque session and server-owned memberships
- invalid credentials and missing, invalid, or expired bearer tokens are rejected
- unassigned organization/workspace pairs are rejected
- viewer may read but may not operate
- owner, admin, and operator may operate
- client-supplied role spoofing is ignored
- missing tenant context rejected for opportunities
- matching tenant context accepted for opportunity creation
- mismatched organization rejected
- vehicle record requires tenant context
- mismatched inventory workspace rejected
- missing tenant context rejected across all list/read endpoints
- cross-tenant opportunity lookup rejected without record disclosure
- cross-tenant procurement linkage rejected
- cross-tenant pick-list linkage rejected
- cross-tenant pick-list availability update rejected without disclosure
- mismatched tenant fields on availability updates rejected
- local browser CORS preflight accepted and non-local origins denied by default
- logout revokes the current local bearer session
- production mode rejects startup without durable database configuration

### Backend RC1 Workflow

Result: passed locally

Validated sequence:

1. Health/startup check.
2. Opportunity create and list.
3. Vehicle create from opportunity and vehicle read.
4. Procurement analysis retrieval.
5. Pick-list create, persisted availability update, and list.
6. Focus-point start and complete.
7. Inventory create and list.

Evidence: `services/api/tests/test_rc1_workflow.py`; 28 tests passed across the
full backend suite.

GitHub Actions confirmation: backend and authenticated core integration passed
on pull-request run `29363414967`.

### Flutter Primary Path

Result: passed in auth/tenant/RBAC CI

Evidence: Pull-request run `29363414967` passed `flutter pub get`,
`flutter analyze`, and `flutter test` at commit
`9bf4490f91b914b05963208355218a863b632977`.

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

Full-path test added at
`apps/recycleros_pro_mobile/test/rc1_workflow_test.dart`. It drives a 430 by 932
mobile viewport through:

1. API credential exchange and server-owned workspace selection.
2. Workspace selection.
3. Mission Control.
4. Opportunity and vehicle creation.
5. Procurement approval.
6. Pick-list availability.
7. Focus-point part selection and completion.
8. Inventory creation.

The app injects `FakeRc1Gateway` into the full mobile test and
asserts all eight workflow calls carry `org-local` and `workspace-local`. A Dio
transport test verifies login response mapping, bearer authorization, required
tenant headers, and API response mapping. A focused widget test verifies that a
failed login stays on the login screen and a viewer cannot create records.

The authenticated `core-integration` job also passed on pull-request run
`29363414967`, completing all eight live transitions with bearer and tenant
context. The new composite `release-evidence` job passed on push run
`29363973050` and pull-request run `29364157746` at commit
`28eab96b8ed1ec8f03b2d4ecda6e1fea1fe5da53`.

### PostgreSQL Restart and Auth Controls

Result: passed in GitHub Actions

`services/api/tests/test_postgres_runtime.py` is installed in the clean
PostgreSQL migration job. It validates:

1. Clean migration through `026_rc1_durable_runtime.sql`.
2. Login and the complete opportunity-to-inventory workflow.
3. Workflow records and the bearer session survive a new app/store/auth instance.
4. Logout revocation survives another app instance.
5. Repeated failed logins trigger a durable lockout.
6. Login, failure, block, and logout audit events are stored.

Evidence: push run `29366652838` and pull-request run `29366685297` passed the
clean PostgreSQL migration and restart job at commit
`7beea835073e42e8f07b90afbf1c4687e972d734`.

### Pilot Runtime and Operations

Result: local checks passed; Linux container and restore evidence pending CI

Local evidence:

- 38 backend tests passed; 1 PostgreSQL-only test skipped
- liveness remains available when dependency readiness fails
- local readiness reports workflow storage and auth independently
- production configuration requires trusted hosts
- secret files are read without accepting ambiguous direct values
- backup commands omit the database password
- restore requires an exact target database confirmation
- generated pilot secrets are never overwritten

GitHub Actions will validate the compose model, build and run the non-root
read-only image, wait for real PostgreSQL/auth readiness, back up populated RC1
data, restore it into a clean database, and verify auth and workflow records.
