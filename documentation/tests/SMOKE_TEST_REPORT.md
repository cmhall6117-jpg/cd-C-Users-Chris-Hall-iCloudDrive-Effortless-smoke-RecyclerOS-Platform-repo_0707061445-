# Smoke Test Report

## Vehicle and Procurement Controls CI

Result on August 29, 2026: passed automated candidate checks; live deployment
and iPhone retest pending.

- Branch: `codex/rc1-vehicle-procurement-controls`
- Draft pull request: `#32`
- Tested commit: `c9e61b5`
- Push run `33247011522`: all RC1 jobs passed
- Pull-request run `33247013038`: all RC1 jobs passed
- Pages run `33247012999`: Flutter web build passed; draft-branch deployment
  skipped
- Backend coverage includes tenant-scoped mileage updates, procurement-decision
  updates, mismatched tenant rejection, and cross-tenant non-disclosure
- Flutter coverage includes mileage editing, all three procurement choices,
  Part Out routing to Pick List, and non-Part-Out routing back to Vehicle Record
- `flutter analyze` and `flutter test`: passed on both RC1 workflow runs
- Field closure still requires deployment and an iPhone test of mileage editing
  plus Sell Whole or Personal Buy / Use

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

Focused evidence: 10 tests passed. The contract validator returned `valid: true`
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

Result on August 9, 2026: the independent backup, clean-target restore, and
live PITR verification passed; remaining recovery operations are partially
blocked.

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
- Railway staging-dump deletion: passed by human operator and verified absent
- cleanup SSH-key removal: passed; final Railway key list empty
- Pro upgrade and PITR enablement: passed
- PostgreSQL repair deployment `ca3c8918-a664-4b6e-b9cc-998c0650ce27`: active
  and successful at 12:44 EDT
- post-redeployment readiness: HTTP 200 with storage and auth ready
- PITR WAL warning clearance: passed
- PITR window advancement: passed, 12:35:54 through 13:19:18
- 164 MB manual native volume backup at 12:34 EDT: passed
- daily schedule every 24 hours with six-day retention: passed
- weekly schedule every seven days with one-month retention: passed
- August 24 scheduled daily snapshots: passed, 485 MB and 472 MB
- August 24 scheduled weekly snapshot: passed, 470 MB
- next scheduled backup: active, due in 14 hours
- automated off-platform retention and cross-device key escrow: not passed

No database password, bearer token, plaintext encryption secret, or plaintext
database archive was written to Git.

## Railway Scheduled Backup Evidence

Result on August 24, 2026: passed for the one-person pilot.

- latest daily backup: completed 9 hours before capture, 485 MB
- prior daily backup: completed 1 day before capture, 472 MB
- weekly backup: completed 1 day before capture, 470 MB
- next scheduled backup: due in 14 hours
- evidence: `documentation/release/evidence/railway/2026-08-24-scheduled-volume-backups.jpg`
- SHA-256: `39d270b2d85de6c5301209e7c43a5bbba85f32f7eb2bb95f21c352a695b82181`

## Railway Monitor Incident Drill

Result on August 9, 2026: passed.

- PR `#15` merged the monitor workflow to `main` at
  `e2b1fee3c83a03daf6aec31d5bf3e354133564b8`
- healthy monitor run `31331712419`: passed
- simulated-failure run `31331739729`: failed as designed
- simulated incident issue `#16`: opened with the triggering run link
- recovery monitor run `31331787276`: passed
- incident issue `#16`: closed as completed with the recovery run link
- two-hour default-branch schedule: active

The incident was synthetic; no Railway resource, credential, database, volume,
PITR setting, or backup schedule was changed.

## Railway Pilot Owner Assignment

Result on August 9, 2026: passed for the one-person pilot.

- restore owner: Chris Hall
- support owner: Chris Hall
- approval source: explicit project-owner approval
- scope: one-person Railway pilot only
- field access: approved for Chris Hall on August 24, 2026
- field approval evidence: `project-owner-approval-2026-08-24`
- second tester: blocked pending a separate durable identity
- protected acceptance: passed in run `32770410381`

No credential, secret, or elevated Railway permission was added by this owner
assignment.

## Railway Protected Acceptance

Result on August 24, 2026: passed for the one-person pilot.

- verified contract and exact deployment identity: passed
- TLS certificate: TLS 1.3, 63 days remaining
- liveness: HTTP 200
- readiness: HTTP 200
- release identity: HTTP 200 for
  `5784f4526e97de7cc60538d00ecc6977ca13a375`
- cache control, referrer policy, content-type, frame, and HSTS headers: present
- interactive docs: HTTP 404
- OpenAPI schema: HTTP 404
- protected workflow: run `32770410381`, all three jobs passed
- policy cleanup: temporary `main` rule removed; original deployment-branch
  rule is the only remaining allowlist entry

The workflow had read-only repository permission and did not provision, deploy,
or mutate any Railway resource.

## Railway One-Person API Field Smoke

Result on August 24, 2026: passed against the live pilot.

- run ID: `20260824212230-5fd820be`
- local backend regression: 72 passed, 2 skipped
- approved release identity: passed
- login and single membership selection: passed
- authenticated identity: passed
- missing tenant context: rejected with HTTP 400
- mismatched tenant context: rejected with HTTP 403
- Mission Control opportunity data: HTTP 200
- opportunity discovery: `OPP-000001`
- vehicle record: `VEH-000001`
- procurement: three scenarios, `partOut` recommended
- pick-list availability: `available`
- Focus Point: completed
- inventory intake: `INV-000001`
- logout: HTTP 204
- revoked session: rejected with HTTP 401
- evidence SHA-256:
  `7ceffa050ddba5a2901ac7794747b8882d105812536c10be24313a1888fc249f`
- credential scan: passed; no credential or token field is present

This result proves the live tenant-scoped API path with synthetic data. It does
not claim a manual Flutter device session; that evidence remains tracked under
`DEF-RAILWAY-006`.

## Operator Credential Recovery Tests

Result on August 26, 2026: recovery candidate passed CI; live rotation was not
required.

- secure prompt, confirmation, and minimum-length tests: passed
- confirmation-email guard: passed
- password absence from command output: passed
- full backend regression: 78 passed, 3 skipped
- source and operational entrypoint compilation: passed
- PostgreSQL integration coverage added for old-password rejection, new-password
  acceptance, session revocation, lockout clearing, and audit-event creation
- PostgreSQL integration execution: skipped locally because no clean database
  runtime is available
- GitHub push run `32957902186` and pull-request run `32957922930`: clean
  PostgreSQL jobs passed, and every job in both 11-job RC1 matrices passed
- the assigned tester recovered the original credential before rotation
- live password rotation: not run; PostgreSQL and the sealed Railway variable
  were intentionally left unchanged
- temporary Railway recovery SSH key: revoked
- temporary local recovery key files: removed

No password, password digest, database URL, session token, or authorization
header was written to repository evidence.

## Railway iPhone UI Field Smoke

Result through August 28, 2026: passed from login through Inventory Intake and
logout for the approved one-person pilot.

- tester: Chris Hall
- device: iPhone running Safari; model and browser version were not evidenced
- frontend: public GitHub Pages pilot
- initial frontend workflow: run `32783845146`, passed
- guarded frontend workflow: run `33061203825`, passed
- guarded frontend commit: `d4e1da2fe6b6f5c29af9de95c2c444445744c69c`
- live API health: HTTP 200, version `0.6.0`
- API release: `e929c9977666b1fc30c7cdecbe30a2dfd3e4feef`
- storage and auth storage: PostgreSQL
- login and authenticated tenant listing: passed
- workspace selection: passed for RecyclerOS Operations
- Mission Control rendering and zero-state metrics: passed
- Opportunity Discovery: synthetic opportunity `OPP-000002` created with a
  blank VIN
- Vehicle Record: linked vehicle `VEH-000002` rendered with its timeline and
  synthetic operating facts
- Procurement: later synthetic opportunity `OPP-000003` rendered three
  scenarios with Part-Out recommended
- Pick List: Part-Out approval queued one synthetic vehicle; Available selection
  enabled Open Focus Point
- Focus Point entry: active KPI timer, confirmed yard and row, five part choices,
  and pre-selection disabled completion rendered
- Focus Point completion: selecting `ECM / PCM` and `LED Headlights` enabled the
  action; completion succeeded and opened Inventory Intake
- Inventory Intake readiness: selected part, storage location `A-12`, Used
  Untested condition, Available status, and enabled Create Inventory rendered
- Inventory item creation: `INV-000002` saved and rendered its ready-for-sync
  confirmation, one-item session count, and Session Inventory entry
- continuity limitation at this point: retained screenshots spanned two
  synthetic attempts; the August 28 continuity run below later resolved it
- observed UI defect: `DEF-RAILWAY-008`, closed after guarded-build retest
- logout: the deployed Mission Control Sign out control returned the iPhone to
  Sign in; automated API coverage proves HTTP 204 and revoked-token HTTP 401
- logout implementation defect: `DEF-RAILWAY-009`, closed after green CI,
  successful Pages deployment, and the live iPhone retest
- evidence manifest:
  `documentation/release/evidence/railway/2026-08-26-iphone-ui-manifest.json`
- workspace screenshot SHA-256:
  `36f9cb40dd788b087cd735d8a84d7df910f99c33989b528db80f6d3f94a28b33`
- Mission Control screenshot SHA-256:
  `245aeaf74b3861a2931face31c9aaccf288b83fdd5c9b62f2c689fc770692579`
- Opportunity creation screenshot SHA-256:
  `09f3ddda7bf057359ab3fa818276487dbd8c9f2fc49c4e3421d91a131ea4b200`
- Vehicle Record screenshot SHA-256:
  `8e0b469288beb077198314d56261eef40b2f1c289170b5734714e51ae8e3232d`
- Procurement screenshot SHA-256:
  `04ceaaf7fa92e06b4c8071b0503c258bf1de53212ac64b935c2652a08a3e1736`
- Pick List awaiting-availability screenshot SHA-256:
  `9a3f09528f84a25f31e92b7c25d2cb77a13ea93b5f8d0693d26d9ae914561ed6`
- Pick List available screenshot SHA-256:
  `907e30f4c76eb197aedb5d155be9226ff099b97a21f04af26a0c6ea430cd7ca2`
- Focus Point entry screenshot SHA-256:
  `65929a03782faf819db560bc7df20715ca03a23167799ce98d43b3c0ad6a0146`
- Focus Point selected screenshot SHA-256:
  `19b6ebb0137247648dd5b521e8ba5ded3d9bf9e78a6c85a29af76b6f678aeaa5`
- Inventory Intake ready screenshot SHA-256:
  `8604b7177dc1c9cdf615ac394945a4df0ebde2fe35f3a95e7801ba7f60d47739`
- Inventory created screenshot SHA-256:
  `619b53c848d990aca8ce8a38f442e3470fa49116db719414c0a4fde720e706da`
- Logout control screenshot SHA-256:
  `bcd024c4526d2bc53e56c443f0284b0e0c26881eab69a2cf14a9ba7c816260f9`
- Logout returned-to-sign-in screenshot SHA-256:
  `391ec645cc7f833514cce861541710e9d8b30f7ead1d9fe00387876e2ce17829`
- duplicate Pick List submission: byte-identical to the retained
  awaiting-availability screenshot and omitted

This closes `DEF-RAILWAY-006` for the approved one-person pilot. At this point
the multi-attempt continuity limitation remained; the August 28 continuity run
below later resolved it. The evidence does not expand to a second tester or
production traffic. No credential, session token, authorization header, or
database URL appears in the retained evidence.

## Flutter Browser Session Guard

Result on August 27, 2026: passed CI, deployment, and live iPhone opportunity
creation retest.

- defect: `DEF-RAILWAY-008`
- trigger: browser reload, iOS tab eviction, or operational deep link without the
  in-memory authenticated workflow state
- prior result: Opportunity Discovery rendered with Create Opportunity disabled
- data mutation: none; the disabled action could not submit the form
- privacy handling: the supplied screenshot is not retained because it may
  contain a real VIN
- fix: route unauthenticated or expired sessions to login and unselected sessions
  to workspace selection
- permission hardening: require a selected workspace and normalize the role
  before enabling write actions
- regression coverage: unauthenticated Opportunity Discovery deep link must
  render login and must not render the New Opportunity form
- local Flutter execution: blocked because this workstation has no Flutter or
  Dart SDK
- corrected CI run `33020582147`: all jobs passed, including Flutter analyze,
  Flutter tests, and the deep-link regression
- GitHub Pages workflow run `33061203825`: build and deploy passed for merge
  commit `d4e1da2fe6b6f5c29af9de95c2c444445744c69c`
- public pilot endpoint after deployment: HTTP 200
- live iPhone result: synthetic opportunity `OPP-000002` created with a blank
  VIN; the active-opportunity card and Create Vehicle Record action rendered
- sanitized screenshot SHA-256:
  `09f3ddda7bf057359ab3fa818276487dbd8c9f2fc49c4e3421d91a131ea4b200`
- defect result: `DEF-RAILWAY-008` closed
- remaining device evidence at that point: logout and revoked-session behavior;
  subsequently completed on August 28 and closed under `DEF-RAILWAY-006` and
  `DEF-RAILWAY-009`

## Flutter Logout Verification

Result on August 28, 2026: passed CI, deployment, and live iPhone execution.

- gateway contract: adds logout without tenant headers
- Dio behavior: sends `POST /v1/auth/logout` with the bearer token and clears the
  token only after HTTP success
- controller behavior: clears the complete workflow state after revocation
- UI behavior: Mission Control exposes an icon-based Sign out command
- failure behavior: keeps the authenticated workspace open and shows the API
  error when revocation fails
- regression coverage: direct Dio request, successful widget logout, failed
  widget logout, and the full RC1 widget path ending at Sign in
- local Flutter execution: blocked because this workstation has no Flutter or
  Dart SDK
- push CI run `33097181838`: passed every RC1 job
- pull-request CI run `33097221722`: passed every RC1 job
- GitHub Pages run `33119763314`: build and deployment passed for merge commit
  `d2eb96d5662318c3e389b02b78b3f84903d4d64f`
- public bundle check: HTTP 200 with both Sign out and `/v1/auth/logout`
- iPhone result: Sign out rendered on Mission Control and returned the client to
  Sign in
- retained evidence: two sanitized screenshots and SHA-256 values in the iPhone
  UI manifest
- defects closed: `DEF-RAILWAY-006` and `DEF-RAILWAY-009`

## Railway Monitor Release Identity Recovery

Result on August 28, 2026: passed.

- prior expected release: `5784f4526e97de7cc60538d00ecc6977ca13a375`
- observed healthy release: `e929c9977666b1fc30c7cdecbe30a2dfd3e4feef`
- latest failed scheduled run: `33180786025`; only release identity failed
- direct health result: HTTP 200 with PostgreSQL storage and auth
- corrected contract/live SHA comparison: exact match
- recovery run `33190365952`: success in 10 seconds
- recovery checks: TLS, liveness, readiness, release identity, security headers,
  hidden docs, and hidden OpenAPI passed
- incident `#24`: automatically closed by the successful workflow
- defect `DEF-RAILWAY-010`: closed

## iPhone Single-Entity Continuity Run

Result on August 28, 2026: passed through Inventory creation.

- displayed session window: 5:34-5:35
- Opportunity creation: `OPP-000007`, blank VIN, synthetic vehicle facts
- active opportunity: `OPP-000007` card rendered with Create Vehicle Record
- Procurement: `OPP-000007` rendered all three scenarios with Part-Out
  recommended
- Focus Point: the same synthetic vehicle rendered with active KPI timer and
  selected ECM / PCM plus LED Headlights
- Inventory: `INV-000004` saved and rendered ready-for-sync plus Session
  Inventory confirmation
- vehicle identifier: not retained
- continuity result: the repeated opportunity identifier and synthetic vehicle
  facts establish one entity path from Opportunity through Inventory
- boundary evidence: login, workspace selection, Vehicle Record behavior, and
  logout remain established by the earlier retained iPhone evidence
- privacy: no credential, real VIN, customer data, token, or GPS metadata is
  present in the six new screenshots
