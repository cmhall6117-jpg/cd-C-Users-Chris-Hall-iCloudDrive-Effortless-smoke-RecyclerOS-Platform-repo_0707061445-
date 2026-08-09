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

Result: passed locally and in Linux CI

Local evidence:

- 38 backend tests passed; 1 PostgreSQL-only test skipped
- liveness remains available when dependency readiness fails
- local readiness reports workflow storage and auth independently
- production configuration requires trusted hosts
- secret files are read without accepting ambiguous direct values
- backup commands omit the database password
- restore requires an exact target database confirmation
- generated pilot secrets are never overwritten

GitHub Actions validated the compose model, built and ran the non-root read-only
image, waited for real PostgreSQL/auth readiness, backed up populated RC1 data,
restored it into a clean database, and verified auth and workflow records.

Evidence: push run `29369194654` and pull-request run `29369197183` completed
those checks successfully at commit
`59bd74a78c39923ad99d583a00f352a57d8dfb95`.

### Production Runtime And Release Controls

Result: full local backend and focused production checks passed; CI pending

Local checks validate:

- production rejects wildcard hosts, HTTP browser origins, and wildcard proxies
- production hides docs and OpenAPI while returning HSTS and API security headers
- health identifies the exact release SHA
- migration runner reads secret files without accepting ambiguous sources
- owner bootstrap requires a 16-character secret and exact email confirmation
- restore rejects a backup whose SHA-256 manifest does not match
- release manifest pins a complete image digest, commit, and all migration files
- production Compose and GitHub Actions workflow parse as valid YAML

The GitHub production container gate will additionally run clean PostgreSQL
migrations, one-time owner provisioning, two Uvicorn workers, readiness, login,
hidden docs, security headers, and release identity in the hardened Linux image.

Final local evidence: Python compilation passed, 46 backend tests passed with 2
PostgreSQL-only tests skipped, and clean SQLite initialization passed all 10
migrations plus tenant-column and mismatch-rejection checks.

GitHub push run `29372078034` and pull-request run `29372080469` passed all
eight jobs at `847a1bed5e9a438d3a85758954abdca1400525a6`, including the
production container, PostgreSQL migration replay, manifest-verified restore,
Flutter analyzer/tests, live core path, and composite release-evidence gate.

### Production Environment Acceptance Contract

Result: focused local checks passed; live target blocked external

Eight tests validate:

- the checked-in example contract is structurally valid with placeholders
- a placeholder contract cannot claim launch readiness
- a complete approved contract passes strict validation
- credential fields and public database access are rejected
- expected public TLS, release, health, security headers, and hidden docs pass
- expiring TLS and a wrong deployed release fail
- managed PostgreSQL requires TLS, a limited role, version 16+, schema readiness,
  active owner/admin membership, and the exact migration checksum ledger
- empty owner fields and non-HTTPS browser origins fail structural validation

Both CI workflow files parse locally. No live endpoint or managed database check
was attempted because provider and environment resources are unselected.

Final local repository evidence: Python compilation passed, 54 backend tests
passed with 2 PostgreSQL-only tests skipped, and SQLite passed all 10 migrations
plus tenant-column and mismatch-rejection checks.

### Google Cloud Pilot Guardrails

Result: contract and Terraform provider checks passed locally and in CI

Evidence:

- `gcp_pilot_contract.py` reported the planned contract structurally valid
- the same report correctly marked field readiness false
- 5 focused tests passed in 0.40 seconds
- credential-like contract fields are rejected
- cost, region, public database, and Cloud Run scale drift are rejected
- Terraform 1.14.6 formatting passed
- the bootstrap root validated against Google provider 7.41.0
- the environment root validated against Google provider 7.41.0 and Random
  provider 3.9.0
- the complete backend suite passed 59 tests with 2 PostgreSQL-only skips
- SQLite initialized cleanly through all 10 migrations and tenant checks
- no Google Cloud resource, credential, or secret was created

Pull-request run `30162538935` independently passed `gcp-pilot-iac`, backend,
SQLite, PostgreSQL migration replay and restore, Flutter analyze/test, live core
integration, both hardened container jobs, and the composite release-evidence
gate at commit `8b24fae4d540834edf0c041a9b06c8d619fa7058`.

### Railway Pilot Configuration

Result: repository configuration passed; live target blocked external

Local checks validate:

- the planned credential-free Railway contract is structurally valid
- the planned contract cannot claim field readiness
- a completed contract can satisfy every readiness requirement
- credential fields, cost drift, scale drift, and public database drift fail
- database and platform variables remain service references, not literal secrets
- acceptance URL and SHA inputs must match the committed deployment identity
- the Docker healthcheck honors Railway's assigned `PORT`
- `railway.json` passes Railway's current official JSON schema

Focused evidence: 9 tests passed. The contract validator returned `valid: true`
and `field_ready: false`, which is the required pre-provisioning result. Python
compilation passed. No live endpoint, database, backup, or billing check was
attempted because no Railway project is approved or provisioned.

Full local regression evidence: 63 backend tests passed with 2 PostgreSQL-only
tests skipped, Python compilation passed, SQLite initialized all 10 migrations,
and both GitHub workflow files parsed successfully.

GitHub evidence: push run `30723893531` and pull-request run `30724007217`
passed all 10 jobs at `fbf1c5f09c5a1d8c69a9f4ca312bf9a189e3fd8f`.
This includes the Railway configuration gate, backend, clean SQLite and
PostgreSQL, populated backup/restore, Flutter analyze/test, live core path,
hardened pilot and production containers, and composite release evidence.

### Railway Live Acceptance

Result on August 2, 2026: first reproducible runtime passed; field-readiness
controls remain blocked.

- `/v1/health/live`: 200, service alive
- `/v1/health/ready`: 200, PostgreSQL storage and auth ready
- `/v1/health`: 200, version `0.6.0`, exact release
  `5784f4526e97de7cc60538d00ecc6977ca13a375`, PostgreSQL storage
- `/docs` and `/openapi.json`: 404 in production mode
- HTTPS HSTS, no-store, no-referrer, nosniff, and frame-deny headers: present
- operator login: 200; durable operator membership returned
- tenant request without organization/workspace headers: 400
- tenant request with mismatched membership: 403
- tenant request with the assigned organization/workspace: 200
- logout: 204
- database migrations: all eleven active files passed before startup
- API and database manifests: one US East replica each
- database public domains: none
- evidence-branch backend regression: 69 passed, 2 PostgreSQL-only skipped
- evidence-branch Python compilation: passed
- updated Railway contract: valid and intentionally not field-ready

The generated password and bearer token remained in memory during acceptance
and were not printed or written to the repository. Backup/restore, continuous
monitoring, alert delivery, and second-tester evidence were not claimed.

## Live Railway Recovery Drill

Result on August 9, 2026: the one-time backup and clean-target restore passed;
ongoing recovery operations remain blocked.

- current backend regression: 70 passed, 2 PostgreSQL-only skipped
- `pg_dump` and source database version: PostgreSQL 16.14
- custom archive: 61,051 bytes and 150 TOC entries
- server/download SHA-256 equality: passed
- clean-target `pg_restore --exit-on-error`: passed
- restored public tables: 24
- restored migration-ledger rows: 11
- restored organization/workspace/user/membership counts: `1/1/1/1`
- encrypted-copy decrypt/hash verification: passed
- temporary restore database removal: passed and verified
- temporary Railway SSH-key removal: passed; final key list empty
- local plaintext and key cleanup: passed
- native schedules, automated retention, cross-device key escrow: not passed
- Railway staging-dump deletion: pending required human command

No database password, bearer token, plaintext encryption secret, or plaintext
database archive was written to Git.
