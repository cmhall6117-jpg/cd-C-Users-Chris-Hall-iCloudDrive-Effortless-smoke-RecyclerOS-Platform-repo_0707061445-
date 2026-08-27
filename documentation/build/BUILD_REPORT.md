# RC1 Build Report

## Repository

- Branch: `codex/gcp-pilot-environment`
- Monorepo root: `repo_0707061445`
- Source package archive: `archive/source_packages`
- Repository inventory: `documentation/repository/REPOSITORY_INVENTORY.md`

## Backend

- FastAPI entrypoint: `services/api/src/main.py`
- Registered routers: health, auth, opportunities, vehicles, procurement, pick list, harvest, inventory
- Auth implementation and boundary: `services/api/src/auth.py`
- Authenticated tenant/RBAC dependency: `services/api/src/tenant.py`
- Injectable storage dependency: `services/api/src/dependencies.py`
- Workflow store contract and local implementation: `services/api/src/store.py`
- PostgreSQL workflow implementation: `services/api/src/postgres_store.py`
- PostgreSQL auth implementation: `services/api/src/postgres_auth.py`
- Durable runtime migration: `database/migrations/postgres/026_rc1_durable_runtime.sql`
- Automated tests include `test_auth_rbac.py`, `test_tenant_isolation.py`, `test_rc1_workflow.py`, and `test_postgres_runtime.py`

Local result:

- Backend requirements are available in the ignored repository `.venv`.
- `python -m compileall services/api/src`: passed.
- FastAPI startup and OpenAPI route manifest check: passed with 14 paths.
- `pytest -q services/api/tests`: 28 passed and 1 PostgreSQL-only test skipped in 14.00 seconds on the current local run.
- SQLite clean initialization: passed all 10 client migrations, tenant-column checks, and tenant mismatch rejection.
- PostgreSQL restart test: passed in GitHub Actions against clean PostgreSQL 16 services.
- PostgreSQL client dependencies were split into `services/api/requirements-postgres.txt` so backend tests and PostgreSQL migration checks can install only the dependencies they need in CI.

Auth/tenant/RBAC baseline CI result:

- Pull-request run `29363414967` passed `python -m compileall src` and the
  complete 26-test backend suite at commit
  `9bf4490f91b914b05963208355218a863b632977`.

## Flutter

- App routes registered in `apps/recycleros_pro_mobile/lib/src/app/app_routes.dart`
- Active path: login, workspace selection, mission control, opportunities, vehicle record, procurement, pick list, focus point, inventory intake
- Shared workflow state: `apps/recycleros_pro_mobile/lib/src/state/rc1_workflow.dart`
- Live transport and bearer-session owner: `apps/recycleros_pro_mobile/lib/src/data/dio_rc1_gateway.dart`
- Injected transport contract: `apps/recycleros_pro_mobile/lib/src/data/rc1_gateway.dart`
- Shared domain dependency: `packages/recycleros_domain`
- Full-path test: `apps/recycleros_pro_mobile/test/rc1_workflow_test.dart`
- Auth/RBAC UI test: `apps/recycleros_pro_mobile/test/auth_rbac_ui_test.dart`

Local result:

- `where flutter`: no executable found.
- `where dart`: no executable found.
- `flutter pub get`, `flutter analyze`, and `flutter test`: blocked locally until an SDK is installed.

Auth/tenant/RBAC baseline CI result:

- Pull-request run `29363414967` passed `flutter pub get`, `flutter analyze`,
  `flutter test`, and the authenticated live Dio-to-FastAPI path.

## CI

GitHub Actions workflow at `.github/workflows/rc1-ci.yml` runs backend, SQLite,
PostgreSQL, Flutter, and authenticated core-integration checks. This branch adds
a final `release-evidence` job that summarizes the exact run, commit, event, and
prerequisite results, then fails unless all five required jobs passed.

The defect-closure candidate upgrades official checkout and Python setup actions
to their Node 24 major versions. The PostgreSQL job now applies migration `026`
and verifies the complete workflow, session persistence, logout revocation,
login throttling, and auth audit records across three app instances.

Defect-closure push run `29366652838` and pull-request run `29366685297`
passed all six jobs at commit
`7beea835073e42e8f07b90afbf1c4687e972d734`. Both runs used
`actions/checkout@v6` and `actions/setup-python@v6` with zero check annotations.

Auth/tenant/RBAC pull-request run `29363414967` passed all five prerequisite
jobs at commit `9bf4490f91b914b05963208355218a863b632977`:

- backend
- sqlite-migrations
- postgres-migrations
- flutter
- core-integration

The composite gate passed on push run `29363973050` and pull-request run
`29364157746` at commit
`28eab96b8ed1ec8f03b2d4ecda6e1fea1fe5da53`.

## Pull Request

Draft pull request #8 is open against `codex/rc1-cicd-release-evidence`:

`https://github.com/cmhall6117-jpg/cd-C-Users-Chris-Hall-iCloudDrive-Effortless-smoke-RecyclerOS-Platform-repo_0707061445-/pull/8`

PR text is available at
`documentation/release/RC1_DEFECT_CLOSURE_PR.md`.

## Pilot Deployment Readiness

- API version: `0.5.0`
- OpenAPI paths: 16
- Pilot image: `services/api/Dockerfile`
- Pilot stack: `deploy/pilot/compose.yml`
- Startup: ordered PostgreSQL migrations, then Uvicorn
- Runtime: non-root image, read-only filesystem, dropped capabilities, no-new-privileges
- Configuration: mounted secret files and required production trusted hosts
- Health: independent liveness and storage/auth readiness probes
- Recovery: custom-format backup, SHA-256 manifest, guarded restore, data verification
- Local backend result: 38 passed and 1 PostgreSQL-only test skipped in 16.85 seconds
- Container, compose, and backup/restore execution: passed in GitHub Actions

Push run `29369194654` and pull-request run `29369197183` passed all seven
required jobs at commit `59bd74a78c39923ad99d583a00f352a57d8dfb95`.
The pilot image built and reached PostgreSQL/auth readiness under a read-only
filesystem with all capabilities dropped. Populated RC1 data was backed up,
restored into a clean database, and verified.

Draft pull request #9 is open against `codex/rc1-defect-closure`:

`https://github.com/cmhall6117-jpg/cd-C-Users-Chris-Hall-iCloudDrive-Effortless-smoke-RecyclerOS-Platform-repo_0707061445-/pull/9`

## Production Launch Preparation

- Branch: `codex/production-launch-preparation`
- API version: `0.6.0`
- Production stack: `deploy/production/compose.yml`
- Runtime: digest-pinned image, external database, separate migrations, two API workers
- Security: exact hosts, HTTPS origins, hidden docs, HSTS, non-root read-only container
- Identity: explicit one-time audited owner bootstrap; no bootstrap secret in API
- Database: advisory-locked checksum ledger and manifest-verified restore
- Release: commit, image digest, and migration checksum manifest
- Focused local result: 13 production and operations tests passed
- Full local backend result: 46 passed and 2 PostgreSQL-only tests skipped
- Python compilation and SQLite clean initialization: passed
- GitHub Actions: all eight jobs passed on push run `29372078034` and
  pull-request run `29372080469` at
  `847a1bed5e9a438d3a85758954abdca1400525a6`

## Production Environment Provisioning Contract

- Branch: `codex/production-environment-provisioning`
- Provider model: cloud-neutral; no billable resources or credentials
- Contract: `deploy/production/environment.example.json`
- Validator: `tools/scripts/production_environment_contract.py`
- Public acceptance: `tools/scripts/production_endpoint_verify.py`
- Database acceptance: `tools/scripts/production_database_verify.py`
- Manual workflow: `.github/workflows/production-environment-acceptance.yml`
- Focused local result: 8 environment acceptance tests passed
- Workflow YAML and placeholder-safe contract validation: passed locally
- Full local backend result: 54 passed and 2 PostgreSQL-only tests skipped
- Python compilation and SQLite clean initialization: passed
- GitHub Actions results: pending exact-head evidence

## Google Cloud Pilot Candidate

- Branch: `codex/gcp-pilot-environment`
- Project: `recyleros-platform` (`728951606960`)
- Region: `us-east4`
- Contract: credential-free, structurally valid, field-ready false
- Focused local result: 5 GCP pilot contract tests passed
- Infrastructure: separate bootstrap and repeatable environment Terraform roots
- Database: private PostgreSQL 16 Enterprise, `db-g1-small`, 25 GiB,
  single-zone pilot, deletion protection, backups, and point-in-time recovery
- Runtime: immutable Cloud Run image, 1 vCPU, 1 GiB, min 0, max 2
- Identity: GitHub Workload Identity Federation; no static account keys
- Deployment: manual protected workflows with exact confirmation phrases
- Terraform 1.14.6 format: passed locally
- Terraform provider validation: both roots passed locally with Google 7.41.0
  and Random 3.9.0
- Full local backend result: 59 passed and 2 PostgreSQL-only tests skipped
- Python compilation: passed
- SQLite initialization: all 10 migrations, tenant columns, and mismatch
  rejection passed
- GitHub Actions: all 10 jobs passed on pull-request run `30162538935` at
  `8b24fae4d540834edf0c041a9b06c8d619fa7058`
- Draft pull request: `#12`
- Google Cloud resources created: none

## Railway Pilot Alternative

- Branch: `codex/railway-pilot-environment`
- Base: `codex/production-environment-provisioning`
- Railway config: `deploy/railway/pilot/railway.json`
- Credential-free contract: `deploy/railway/pilot/pilot.contract.json`
- Variable references: `deploy/railway/pilot/variables.example`
- Validator: `tools/scripts/railway_pilot_contract.py`
- Manual acceptance: `.github/workflows/railway-pilot-acceptance.yml`
- Runtime: one US East replica, one worker, 512 MiB memory limit, serverless sleep
- Database: private PostgreSQL 16 reference; public TCP proxy disabled at rest
- Focused local result: 10 Railway tests passed
- Official Railway JSON schema validation: passed locally
- Planned contract validation: passed and correctly reported `field_ready: false`
- Live project, backup, endpoint, monitoring, and cost-control evidence: blocked external
- Full local backend result: 63 passed and 2 PostgreSQL-only tests skipped
- Python compilation and SQLite clean initialization: passed
- GitHub Actions: all 10 jobs passed on push run `30723893531` and
  pull-request run `30724007217` at
  `fbf1c5f09c5a1d8c69a9f4ca312bf9a189e3fd8f`
- Draft pull request: `#13` against `codex/production-environment-provisioning`

## Railway First Reproducible Build

- Date: August 2, 2026
- Provider project: `recycleros-pilot`
  (`22bdb278-c849-4c65-bd93-0031053344a1`)
- Source branch: `codex/railway-pilot-environment`
- Source commit: `5784f4526e97de7cc60538d00ecc6977ca13a375`
- API deployment: `9ccd3586-b57f-4567-937f-0a6864d0d624`, successful
- PostgreSQL deployment: `9a092ef2-5f58-4cc8-92db-03f0af74b8d5`, successful
- Runtime: one US East instance, 512 MiB, one CPU, one worker, serverless sleep
- Database: PostgreSQL 16.14, private networking, 5 GiB persistent volume
- Public endpoint: `https://recycleros-api-pilot.up.railway.app`
- Wait for CI: enabled with one valid GitHub check suite
- Evidence-branch backend regression: 69 passed, 2 PostgreSQL-only skipped
- Evidence-branch Python compilation: passed
- Evidence baseline: `f3b732f5c75bc0c9088b1deefbd3f9149ac220a7`
- Evidence CI: all 22 checks passed on push run `31314925876` and pull-request
  run `31315025909` for draft pull request `#15`
- Updated Railway contract validation: `valid: true`, `field_ready: false`
- Remaining release blockers at that evidence point: field approval and a
  separate second-tester identity. Off-platform automation and cross-device key
  escrow remain hardening work for broader use.

## Railway Recovery Drill

- Date: August 9, 2026
- Current backend regression: 70 passed, 2 PostgreSQL-only skipped
- Source: live private Railway PostgreSQL 16.14 service
- Archive: custom format, 61,051 bytes, 150 TOC entries
- Archive SHA-256:
  `665035b1502c52ba4e80272073b1a8f5a2ee6d5bd4c22a1ff76bfe76a65d704f`
- Download verification: passed; server and workstation hashes matched
- Clean restore: passed into `recycleros_restore_verify_a65d704f`
- Restored schema: 24 public tables and 11 migration-ledger rows
- Restored pilot identity data: organization, workspace, user, and membership
  counts each equal to 1
- Encryption verification: passed; decrypted archive hash matched the source
- Retained encrypted SHA-256:
  `96102505a31888c5c3e9eb2424dae58ef0323747d81b6e126466bbd3da4c1a00`
- Cleanup: temporary database removed, local plaintext removed, temporary
  Railway SSH access revoked and verified empty
- Human cleanup: owner-only Railway staging dump deleted and verified absent;
  cleanup SSH key revoked, local files removed, and final key list empty
- Railway plan: Pro as of August 9, 2026; expected monthly minimum USD 20
- PITR repair deployment: `ca3c8918-a664-4b6e-b9cc-998c0650ce27`, active and
  successful at 12:44 EDT
- PITR result: WAL warning cleared and recovery window advanced from 12:35:54
  through 13:19:18
- Post-redeployment readiness: HTTP 200; storage and auth both ready
- Native volume backup: 164 MB manual snapshot completed at 12:34 EDT
- Native schedules: Daily every 24 hours with six-day retention and Weekly
  every seven days with one-month retention; next backup due in six hours
- Restore owner: Chris Hall, approved for the one-person pilot on August 9
- Scheduled execution evidence on August 24: daily snapshots of 485 MB and
  472 MB, plus a weekly snapshot of 470 MB; next run due in 14 hours
- Gate result: independent restore, live PITR, native scheduled execution, and
  recovery ownership passed for the one-person pilot

## Railway Monitor Activation

- Date: August 9, 2026
- Integration PR: `#15`, merged to `main`
- Merge commit: `e2b1fee3c83a03daf6aec31d5bf3e354133564b8`
- Healthy monitor: run `31331712419`, passed
- Simulated incident: run `31331739729`, expected failure
- Incident delivery: issue `#16` opened by GitHub Actions
- Recovery monitor: run `31331787276`, passed
- Recovery handling: issue `#16` closed as completed with a recovery comment
- Schedule: active every two hours on the default branch
- Support owner: Chris Hall, approved for the one-person pilot on August 9
- Field tester: Chris Hall, approved as the only tester on August 24
- Contract: lifecycle `verified`, `maximum_testers: 1`, approval evidence
  `project-owner-approval-2026-08-24`
- Gate result: uptime, readiness-incident delivery, support ownership, and
  one-person field approval passed

## Railway Protected Acceptance

- Date: August 24, 2026
- Approval implementation: commit `6bf00e29b21d7664b972cc940d79bd7178cf6a60`
- Pull request: `#19`, merged to `main`
- Merge commit: `e99fc294acffc69e078f134ab38344caf2d7401f`
- Full CI: push run `32733071474` and pull-request run `32733139755`; all 10
  jobs passed on both trigger paths
- Protected acceptance: run `32770410381`, passed
- Contract job: lifecycle, one-tester cap, field approval, endpoint, and release
  identity validation passed
- Public endpoint: TLS 1.3 with 63 certificate days remaining; liveness,
  readiness, and release identity returned HTTP 200
- Surface hardening: required security headers present; docs and OpenAPI
  returned HTTP 404
- Environment cleanup: temporary `main` allowlist policy removed; only
  `codex/railway-pilot-environment` remains allowed
- Gate result: passed for one named Railway field tester

## Railway One-Person API Field Smoke

- Date: August 24, 2026
- Run ID: `20260824212230-5fd820be`
- Tester: `operator@effortlesssmoke.com`
- Tenant: `org-local` / `workspace-local`, operator role
- Release: `5784f4526e97de7cc60538d00ecc6977ca13a375`
- Result: all 18 live checks passed
- Local backend regression: 72 passed, 2 skipped
- Working path: login, membership selection, Mission Control data,
  opportunity, vehicle, procurement, pick list, Focus Point, inventory, logout
- Tenant isolation: missing context rejected with HTTP 400; mismatched context
  rejected with HTTP 403
- Session isolation: logged-out token rejected with HTTP 401
- Created synthetic records: `OPP-000001`, `VEH-000001`, `INV-000001`
- Evidence: `documentation/release/evidence/railway/2026-08-24-one-person-field-smoke.json`
- Evidence SHA-256:
  `7ceffa050ddba5a2901ac7794747b8882d105812536c10be24313a1888fc249f`
- Credential scan: no password, token, authorization header, secret, or
  database URL present
- Remaining evidence gap: manual Flutter device interaction under
  `DEF-RAILWAY-006`

## Railway Operator Credential Recovery and iPhone Evidence

- Date: August 26, 2026
- Branch: `codex/railway-operator-credential-recovery`
- Added a no-echo durable password-rotation command to the API image
- Rotation transaction replaces the PBKDF2 credential, revokes active sessions,
  clears login lockouts, and writes a non-secret audit event
- `python -m compileall` plus entrypoint `py_compile`: passed
- Full local backend regression: 78 passed, 3 PostgreSQL-only skipped
- Local PostgreSQL execution: unavailable because this workstation has no
  Docker runtime or configured `DATABASE_URL`
- GitHub push run `32957902186` and pull-request run `32957922930`: all 11 jobs
  passed, including clean PostgreSQL rotation coverage and pilot image packaging
- Live Railway mutation: not performed; the assigned tester recovered and
  successfully used the original credential
- Credential state: PostgreSQL and sealed Railway variable unchanged
- Recovery access cleanup: temporary Railway SSH key revoked and temporary local
  key files removed
- Credential defect: `DEF-RAILWAY-007` closed
- iPhone UI smoke: login, workspace selection, and Mission Control passed
- Flutter web deployment: workflow run `32783845146`, commit
  `9c3814c07cab4d5c1c4301f8bf198aab5d310c36`
- Live API health: version `0.6.0`, release
  `e929c9977666b1fc30c7cdecbe30a2dfd3e4feef`, PostgreSQL storage and auth
- Device-session gate: `DEF-RAILWAY-006` remains open for Opportunity Discovery
  through Inventory Intake and logout
- Evidence:
  `documentation/release/evidence/railway/2026-08-26-iphone-ui-manifest.json`

## Flutter Browser Session Guard

- Date: August 26, 2026
- Branch: `codex/railway-pilot-full-ui-acceptance`
- Defect: `DEF-RAILWAY-008`
- Added operational-route guards for missing, expired, and workspace-unselected
  session state
- Hardened write permission to require workspace selection and a normalized
  owner, admin, or operator role
- Added an unauthenticated Opportunity Discovery deep-link widget regression
  test
- Updated the iPhone runbook with in-memory session recovery behavior
- Local Flutter analyze/tests: not run; Flutter and Dart are unavailable on this
  workstation
- Corrected CI run `33020582147`: all jobs passed, including Flutter analyze,
  Flutter tests, backend, migrations, tenant isolation, and release evidence
- Pull request `#26`: merged as
  `d4e1da2fe6b6f5c29af9de95c2c444445744c69c`
- GitHub Pages workflow run `33061203825`: build and deploy passed
- Public pilot endpoint: HTTP 200 after deployment
- iPhone retest: synthetic opportunity `OPP-000002` created with a blank VIN;
  Create Vehicle Record rendered enabled
- Defect `DEF-RAILWAY-008`: closed on August 27, 2026
- Broader device-session gate `DEF-RAILWAY-006`: remains open for Vehicle Record
  through Inventory Intake and logout
