# Defect Register

## Critical

### DEF-RC1-001: PostgreSQL migration gate blocked locally

Status: closed by CI evidence

Evidence: `docker compose up -d postgres` failed because `docker` is not recognized as a command. Earlier `docker --version` and `psql --version` checks timed out.

Impact: PostgreSQL migrations have not been executed against a local clean database.

Resolution: GitHub Actions `postgres-migrations` succeeded on run `29289307269`.

### DEF-RC1-002: Backend dependency installation is not reproducible locally yet

Status: closed

Evidence: `pip install -r services/api/requirements.txt` timed out after the `psycopg` pin was corrected.

Impact: FastAPI startup import and automated pytest execution could not be completed locally.

Resolution: Backend requirements installed successfully in the ignored repository `.venv` on July 14, 2026. The local backend suite then passed all 13 tests. PostgreSQL-only dependencies remain split into `services/api/requirements-postgres.txt`.

## High

### DEF-RC1-010: Auth identities, memberships, and sessions are process-local

Status: closed by CI evidence

Evidence: `PostgresAuthService` stores identities, memberships, token digests,
expiry, revocation, login attempts, and audit events in PostgreSQL. The restart
test passed on push run `29366652838` and pull-request run `29366685297`.

Impact: None remaining for the RC1 durable auth/session gate.

Resolution: A bearer session remained valid across a fresh auth/app instance,
then logout revocation remained effective across another fresh instance.

### DEF-RC1-008: Core Flutter API integration awaits CI verification

Status: closed by CI evidence

Evidence: The workstation has no Flutter or Dart executable, so the new Dio
gateway, asynchronous workflow controller, and injected fake tests cannot be
analyzed or executed locally.

Impact: None remaining for the reproducible Flutter build gate.

Resolution: An initial analyzer warning was corrected in commit `71c2aa9`.
GitHub Actions PR run `29325554779` then passed `flutter pub get`,
`flutter analyze`, `flutter test`, and the live Flutter-to-FastAPI smoke test.

### DEF-RC1-007: Backend records are not durable across process restarts

Status: closed by CI evidence

Evidence: FastAPI selects `PostgresStore` when `DATABASE_URL` is configured and
production mode fails closed without it. The complete opportunity-to-inventory
workflow survived fresh store/app instances on push run `29366652838` and
pull-request run `29366685297`.

Impact: None remaining for the RC1 durable workflow gate.

Resolution: Migration `026` and `test_postgres_runtime.py` passed against clean
PostgreSQL 16 services in both trigger paths.

### DEF-RC1-003: Flutter SDK is unavailable locally

Status: closed by CI evidence

Evidence: `where flutter` and `where dart` found no executable on July 14, 2026. Earlier Flutter commands timed out without usable output.

Impact: The Flutter baseline cannot run `flutter pub get`, `flutter analyze`, or `flutter test` locally.

Resolution: GitHub Actions completed `flutter pub get`, `flutter analyze`, and `flutter test` successfully on run `29323035764`. Install a local Flutter SDK separately if workstation execution is required.

### DEF-RC1-004: Standard `python -m compileall` hangs locally

Status: closed

Evidence: `python -m compileall services/api/src` emitted compile activity but did not exit before timeout. A previous backend syntax check passed before the environment degraded.

Impact: RC1 cannot mark the requested compile gate passed with clean command completion.

Resolution: The bundled Python runtime completed `python -m compileall services/api/src` locally on July 14, 2026. GitHub Actions also succeeded on run `29289307269`.

## Medium

### DEF-RC1-011: Local auth lacks production account defenses

Status: closed for RC1 scope by CI evidence

Evidence: The PostgreSQL provider verifies PBKDF2 password hashes, rate-limits
failed logins, expires and revokes opaque sessions, exposes logout, and records
auth audit events. Refresh, password recovery, and live SSO remain intentionally
deferred behind `AuthService`.

Impact: No RC1 implementation blocker remains; enterprise identity capabilities
are outside this release scope.

Resolution: Durable lockout, revocation, expiry storage, and auth audit checks
passed on runs `29366652838` and `29366685297`. Refresh, password recovery, and
live SSO remain out of RC1 scope rather than release-gate defects.

### DEF-RC1-009: GitHub Actions use versions targeting deprecated Node.js 20

Status: closed by CI evidence

Evidence: The workflow uses `actions/checkout@v6` and
`actions/setup-python@v6`. Push run `29366652838` and pull-request run
`29366685297` passed all jobs with zero check annotations.

Impact: None remaining.

Resolution: Both official actions ran their Node 24 majors without the prior
Node 20 warning annotations.

### DEF-RC1-006: Draft pull request cannot be opened without a GitHub remote

Status: closed

Evidence: PR #1 is open as draft at `https://github.com/cmhall6117-jpg/cd-C-Users-Chris-Hall-iCloudDrive-Effortless-smoke-RecyclerOS-Platform-repo_0707061445-/pull/1`.

Impact: None remaining for draft PR creation.

Resolution: GitHub CLI confirmed PR #1 is open, draft, and targeting `main` from `codex/rc1-repository-integration`.

### DEF-RC1-005: Generated migration number gap is preserved

Status: accepted risk

Evidence: Active migrations go from `006` to `022`.

Impact: Numbering is non-contiguous, but no duplicate migration numbers are active.

Next action: Keep the manifest explicit and avoid renumbering generated historical packages.

## Pilot Deployment Readiness

### High

#### DEF-PILOT-001: Public ingress, DNS, and TLS are not provisioned

Status: open, external blocker

Evidence: The pilot compose stack intentionally binds API and PostgreSQL ports
to loopback. No public hostname, certificate, or reverse proxy is configured.

Impact: Remote pilot access must not begin.

Next action: Provision the selected provider's approved ingress, DNS, and TLS
endpoint, then record external verification evidence.

#### DEF-PILOT-002: Real pilot secrets are not provisioned

Status: open, external blocker

Evidence: The repository contains secret references and safe creation tooling,
but no live values or approved access record.

Impact: A real pilot environment cannot be started securely.

Next action: Provision secrets in the selected provider's approved secret store,
restrict deployment access, import the operator credential into the approved
password manager, and record rotation ownership.

#### DEF-PILOT-003: Off-host backup operations are not configured

Status: open, external blocker

Evidence: Backup and restore tooling exists, but no encrypted destination,
schedule, retention job, or restore owner is configured.

Impact: A data-bearing pilot would lack an evidenced recovery process.

Next action: Approve recovery targets, configure provider-native and encrypted
off-platform backups, assign the restore owner, and complete a clean-target
restore rehearsal.

### Medium

#### DEF-PILOT-004: Central logs and readiness alerts are not routed

Status: open, external blocker

Evidence: The API exposes liveness and readiness, but no external log collector,
monitor, or alert recipient is configured.

Impact: An unattended pilot failure may not reach an operator promptly.

Next action: Connect runtime logs and readiness probes to the selected provider's
approved monitoring channel and test alert delivery.

#### DEF-PILOT-005: Pilot container and recovery checks await CI

Status: closed by CI evidence

Evidence: Local Python checks pass. Push run `29369194654` and pull-request run
`29369197183` passed the hardened container and populated backup/restore jobs.

Impact: None remaining for repository-level pilot readiness.

Resolution: The Linux image reached real readiness with a read-only filesystem,
dropped capabilities, and no-new-privileges. The recovery rehearsal restored and
verified auth, opportunity, and inventory data.

#### DEF-PILOT-006: GCP Terraform definitions await provider validation

Status: closed by CI evidence

Evidence: A checksum-verified portable Terraform 1.14.6 initialized Google
provider 7.41.0 and Random provider 3.9.0. Formatting passed and both the
bootstrap and environment roots returned `Success! The configuration is valid.`

Impact: No provider-schema blocker remains. Billable infrastructure still must
not be applied until the external approval gates pass.

Resolution: `gcp-pilot-iac` passed contract validation, Terraform formatting,
and both provider roots on pull-request run `30162538935` at
`8b24fae4d540834edf0c041a9b06c8d619fa7058`.

#### DEF-PILOT-007: Billing and budget controls are not evidenced

Status: open, external blocker

Evidence: Project ID and number are recorded, but billing linkage and USD 100
budget alert delivery have not been verified.

Impact: Billable infrastructure must not be applied.

Next action: Link the approved billing account, configure 50%, 80%, and 100%
alerts, verify the recipients, and record the evidence without storing billing
credentials in the repository.

#### DEF-PILOT-008: Keyless deployment trust is not bootstrapped

Status: open, external blocker

Evidence: Workload Identity Federation, state storage, and least-scope deployer
definitions exist under `deploy/gcp/pilot/bootstrap`, but no bootstrap output or
protected GitHub environment is recorded.

Impact: GitHub cannot safely plan or apply the pilot environment.

Next action: Apply the bootstrap once from an authenticated administrator
session, create the protected `gcp-pilot` environment, and record its three
non-secret output variables.

## Railway Pilot Environment

### High

#### DEF-RAILWAY-001: Railway account, project, and budget controls are absent

Status: closed on August 2, 2026

Evidence: Pro project `recycleros-pilot`
(`22bdb278-c849-4c65-bd93-0031053344a1`) is private, account MFA and a passkey
are enabled, and the USD 20 warning plus USD 30 hard limit are active. The
project owner upgraded from Hobby to Pro on August 9, 2026, to activate native
recovery controls; the expected monthly minimum is now USD 20.

Impact: The cost-bounded pilot account prerequisite is satisfied.

Next action: Retain monthly usage evidence and test warning delivery before
field access.

#### DEF-RAILWAY-002: Railway runtime, domain, and sealed variables are absent

Status: closed on August 2, 2026

Evidence: PostgreSQL deployment `9a092ef2-5f58-4cc8-92db-03f0af74b8d5` and API
deployment `9ccd3586-b57f-4567-937f-0a6864d0d624` are successful in US East.
The API is available at `https://recycleros-api-pilot.up.railway.app`, reports
release `5784f4526e97de7cc60538d00ecc6977ca13a375`, uses private PostgreSQL, and
has a sealed generated operator credential. The database has no public domain.

Impact: Remote runtime, login, and tenant acceptance can run.

Next action: Preserve exact release and endpoint evidence for each deployment.

#### DEF-RAILWAY-003: Off-platform recovery automation remains manual

Status: open, non-blocking pilot hardening

Evidence: PostgreSQL 16 is pinned to private 5 GiB US East volume
`postgres-volume-gHwe`. On August 9, 2026, the owner upgraded to Pro and enabled
PITR. An initial invalid-WAL-archive-credential warning was repaired by
redeploying only PostgreSQL as deployment
`ca3c8918-a664-4b6e-b9cc-998c0650ce27`. Railway marked the deployment active and
successful at 12:44 EDT; the volume remained attached, the warning cleared, and
the recovery window advanced from 12:35:54 through 13:19:18. The API readiness
endpoint then returned HTTP 200 with storage and auth ready. Evidence images are
retained under `documentation/release/evidence/railway/`.

The volume-backup panel also shows a successful 164 MB manual backup at 12:34
EDT and an active schedule with its next backup due in six hours. Schedule
configuration confirms Daily is enabled every 24 hours with six-day retention
and Weekly is enabled every seven days with one-month retention. Monthly is
intentionally disabled. On August 24, live backup history showed two completed
daily-schedule snapshots at 485 MB and 472 MB, a completed weekly-schedule
snapshot at 470 MB, and the next scheduled run due in 14 hours. Earlier on
August 9, a PostgreSQL 16.14 custom dump was copied off-platform, its
server and downloaded SHA-256 values matched, and its encrypted copy was
retained outside Git. A clean-target restore passed with 24 public tables, 11
migration-ledger rows, and expected pilot identity records. The temporary
restore database was dropped, local plaintext and SSH keys were removed, and
Railway reported no registered SSH keys. A human operator then deleted the
owner-only staging dump, verified its absence, revoked the cleanup SSH key,
removed its local files, and confirmed that Railway again reported no
registered keys. On August 9, the project owner explicitly assigned Chris Hall
as restore owner for the one-person pilot. Automated off-platform cadence and
cross-device key escrow remain unverified.

Impact: The one-person pilot has PITR, proven native daily/weekly execution, one
independent restore point, and assigned ownership. Off-platform automation and
cross-device key escrow remain defense-in-depth work before broader use.

Next action: Automate off-platform cadence and retention, escrow the recovery
key, and approve the RPO/RTO before expanding beyond the one-person pilot.

### Medium

#### DEF-RAILWAY-004: Railway protected acceptance awaits final execution

Status: closed on August 24, 2026

Evidence: The protected GitHub `railway-pilot` environment exists and Railway
Wait for CI is enabled with one valid check suite. PR `#15` merged the monitor
to `main` as commit `e2b1fee3c83a03daf6aec31d5bf3e354133564b8`. Healthy
workflow run `31331712419` passed. Simulated-failure run `31331739729` failed as
designed and opened incident `#16`. Recovery run `31331787276` passed and
closed that same incident with a recovery comment. The two-hour schedule is
active on the default branch. On August 9, the project owner explicitly assigned
Chris Hall as support owner for the one-person pilot. On August 24, the project
owner approved Chris Hall as the only field tester and recorded evidence
`project-owner-approval-2026-08-24` in the verified contract. PR `#19` merged
the verified one-person contract to `main` as
`e99fc294acffc69e078f134ab38344caf2d7401f` after push run `32733071474` and
pull-request run `32733139755` passed all 10 jobs. Protected acceptance run
`32770410381` then passed contract, public-endpoint, and evidence jobs. The live
endpoint returned HTTP 200 for liveness, readiness, and release identity; TLS
1.3 had 63 days remaining, required security headers were present, and docs and
OpenAPI returned HTTP 404.

Impact: None remaining for the one-person Railway field-access gate.

Resolution: A temporary `main` environment allowlist rule enabled the read-only
protected run and was removed afterward. Verification showed that the original
`codex/railway-pilot-environment` rule is again the environment's only allowed
branch.

#### DEF-RAILWAY-005: A second field tester lacks a separate account path

Status: open, scope limitation

Evidence: The existing pilot bootstrap creates one durable local operator and
the project has no user-administration workflow in the active RC1 path.

Impact: One named tester can be assigned; a second must not share credentials.

Next action: Pilot with one named operator or separately approve a minimal,
audited account-provisioning operation before adding the second tester.

#### DEF-RAILWAY-006: Manual Flutter device field session is not evidenced

Status: closed on August 28, 2026

Evidence: Live synthetic API run `20260824212230-5fd820be` passed all 18 checks
from login through inventory intake and session revocation. Flutter analyze,
widget tests, and live local gateway integration pass in CI. On August 26, 2026,
Chris Hall completed login and workspace selection on an iPhone and reached
Mission Control through the public GitHub Pages build. The frontend is tied to
successful workflow run `32783845146` at commit
`9c3814c07cab4d5c1c4301f8bf198aab5d310c36`; the live Railway health response
reported API release `e929c9977666b1fc30c7cdecbe30a2dfd3e4feef`, PostgreSQL
storage, and PostgreSQL auth. The screenshots and checksums are recorded in
`documentation/release/evidence/railway/2026-08-26-iphone-ui-manifest.json`.
On August 27, the guarded Pages build created synthetic opportunity `OPP-000002`
and linked vehicle `VEH-000002` on the iPhone. The Vehicle Record rendered its
tenant-linked timeline and synthetic operating facts. A later synthetic attempt
at `OPP-000003` rendered three Procurement scenarios, created a queued Pick List
vehicle, persisted its Available selection, and opened Focus Point with the KPI
timer active. The manifest records that the retained screenshots do not prove
one uninterrupted entity chain across both synthetic attempts. Selecting
`ECM / PCM` and `LED Headlights` enabled and completed Focus Point, and Inventory
Intake opened with the expected selected part and defaults. Create Inventory
then saved `INV-000002` and rendered its ready-for-sync confirmation and Session
Inventory entry.

On August 28, PR `#28` had passed every push and pull-request CI job and Pages
deployment `33119763314` had deployed merge commit
`d2eb96d5662318c3e389b02b78b3f84903d4d64f`. After clearing Safari's cached
website data for the Pages origin, the iPhone rendered the new Sign out command.
Selecting it returned the client to Sign in. The retained screenshots establish
the manual UI transition; existing automated API and Flutter coverage establish
HTTP 204 logout, subsequent HTTP 401 rejection of the revoked token, and client
state clearing after successful revocation.

Impact: None remaining for the one-person Railway pilot. Manual stage behavior
is evidenced from login through Inventory Intake and logout. The retained
screenshots span more than one synthetic attempt and therefore do not claim one
uninterrupted entity chain across every image.

Resolution: Close the device evidence gate for the approved one-person pilot.
At closure, the multi-attempt continuity note and single-tester limit remained
explicit scope constraints. The continuity follow-up below removes the former;
the single-tester and broader production limits remain.

Continuity follow-up: On August 28, the tester submitted six sanitized images
from one displayed 5:34-5:35 session. They establish synthetic opportunity
`OPP-000007` with a blank VIN through Procurement, Focus Point, and inventory
`INV-000004`. The Vehicle Record identifier was not retained, so the evidence
uses the repeated synthetic title, year, make, model, and opportunity identifier
to establish entity continuity. Login, workspace selection, Vehicle Record
behavior, and logout remain separately evidenced. This removes the prior
multi-attempt entity-chain limitation without expanding the one-person scope.

#### DEF-RAILWAY-007: The sealed pilot operator credential is unavailable

Status: closed

Evidence: On August 26, 2026, the assigned tester reported that the operator
password was not present in the approved password manager. Railway holds
`RECYCLEROS_LOCAL_OPERATOR_PASSWORD` as a sealed variable, so its value cannot
be retrieved. Recovery-candidate push run `32957902186` and pull-request run
`32957922930` passed every RC1 job, including clean PostgreSQL rotation tests.
Before rotation, the assigned tester recovered the original credential and used
it successfully to reach the authenticated workspace selector and Mission
Control on an iPhone. No database credential or sealed Railway variable was
changed. The temporary recovery SSH key was revoked and all temporary local key
files were removed.

Impact: None remaining. The original durable credential and sealed Railway value
remain synchronized, and the manual Flutter device session can continue.

Resolution: Retain the tested recovery command as a controlled contingency. Do
not rotate the live credential unless the approved owner initiates a future
recovery event.

#### DEF-RAILWAY-008: Browser reload opens an operational form without session context

Status: closed on August 27, 2026

Evidence: On August 26, 2026, an iPhone field session reopened Opportunity
Discovery with populated local form fields while Create Opportunity remained
disabled. The button is disabled only while the workflow is busy or the selected
workspace role cannot operate. Code review confirmed that a browser reload loses
the in-memory session and workspace role, while the router previously allowed
the operational deep link to render without authentication. No create request
was possible, so the entered form values were not submitted to the API. The
submitted screenshot is not retained because it may contain a real VIN.

Impact: iOS tab eviction, browser refresh, or reopening an operational URL can
strand a field operator on a read-only-looking form with no explanation, blocking
the primary working path.

Resolution: PR `#26` guarded all operational routes. Unauthenticated or expired
sessions return to login, authenticated sessions without a selected workspace
return to workspace selection, and write permission requires a selected
workspace plus a normalized owner, admin, or operator role. Corrected CI run
`33020582147` passed all jobs, including Flutter analyze, Flutter tests, and the
unauthenticated deep-link regression. GitHub Pages workflow run `33061203825`
deployed merge commit `d4e1da2fe6b6f5c29af9de95c2c444445744c69c`.

Live verification: On August 27, Chris Hall signed in again on the deployed
build and created synthetic opportunity `OPP-000002` with a blank VIN. The
active-opportunity card and enabled Create Vehicle Record action rendered. The
sanitized screenshot and checksum are recorded in the iPhone evidence manifest.

#### DEF-RAILWAY-009: Flutter field operator cannot log out

Status: closed on August 28, 2026

Evidence before resolution: The live iPhone path reached Inventory Intake and
created `INV-000002`, but the Flutter UI exposed no logout control. Repository
inspection confirmed no logout or sign-out action in the mobile screens, no
logout method on `Rc1Gateway`, and no client call to the existing backend
`POST /v1/auth/logout` endpoint. Backend automated coverage already proves that
this endpoint returns HTTP 204 and rejects the revoked bearer session afterward.

Prior impact: A field operator could not intentionally revoke the current
session from the browser UI. Closing the tab only discarded in-memory client
state and was not evidence of server-side revocation, so the final
device-session gate could not pass.

Resolution: PR `#28` added a bearer-authenticated gateway call to
`POST /v1/auth/logout`, clears all client workflow state only after successful
revocation, and exposes an icon-based Sign out command on Mission Control. Dio,
fake-gateway, success, failure, and full-workflow widget coverage verify the
request header, token clearing, state clearing, and failure preservation. Push
run `33097181838` and pull-request run `33097221722` passed every RC1 job.
GitHub Pages deployment `33119763314` deployed merge commit
`d2eb96d5662318c3e389b02b78b3f84903d4d64f`. On August 28, the iPhone displayed
Sign out and returned to Sign in after it was selected. Non-secret screenshots
and checksums are retained in the iPhone evidence manifest.

#### DEF-RAILWAY-010: Scheduled monitor expected a superseded API release

Status: closed on August 28, 2026

Evidence: Scheduled monitor runs from `32961483830` through `33180786025`
reported release-identity failure and maintained incident `#24`. The latest
failed report showed TLS 1.3, HTTP 200 liveness and readiness, every required
security header, and hidden docs/OpenAPI; only release identity failed. The
contract expected original release
`5784f4526e97de7cc60538d00ecc6977ca13a375`, while the live `/v1/health`
payload reported healthy release
`e929c9977666b1fc30c7cdecbe30a2dfd3e4feef` with PostgreSQL storage and auth.

Impact: The endpoint remained available and healthy, but the intentionally
strict monitor correctly blocked field-access status because repository release
expectations had drifted from the deployed API.

Resolution: Synchronize `runtime.release_commit` with the exact deployed SHA
and require that update for every future Railway API deployment. Read-only
workflow run `33190365952` passed the full public-surface verification in 10
seconds and automatically closed incident `#24` with a recovery comment. The
contract now records that recovery run as current monitor evidence.

#### DEF-RAILWAY-011: Vehicle and procurement choices are display-only

Status: fix implemented; CI passed on August 29, 2026; deployment and field
retest pending

Evidence: During the iPhone pilot, Vehicle Record displayed a hardcoded mileage
without an edit action. Procurement rendered Resale, Personal Use, and Part-Out
scenarios, but the cards were not selectable and the only approval command
always created a Part-Out Pick List item.

Impact: A field operator cannot record actual vehicle mileage or choose Sell
Whole or Personal Buy / Use. The UI can therefore persist the wrong operating
intent and incorrectly force a vehicle into the dismantling workflow.

Resolution in progress: The existing VS-002 and VS-003 path now includes
tenant-scoped mileage and procurement-decision updates. Mileage opens a
validated numeric editor. Procurement outcomes are selectable, persist the
chosen intent, and use outcome-specific actions. Only Part Out proceeds to Pick
List; Sell Whole and Personal Buy / Use return to Vehicle Record with the saved
intent visible. Backend, PostgreSQL, tenant-isolation, Dio, fake-gateway, live
gateway, and Flutter workflow coverage are included.

CI evidence: commits `12817f7`, `9bc8c7d`, and `c9e61b5` passed the complete
push run `33247011522` and pull-request run `33247013038`. This includes
backend, clean PostgreSQL, SQLite, tenant-isolation, Flutter analyze, Flutter
test, connected integration, container, environment-contract, and composite
release-evidence jobs. Pages run `33247012999` built the Flutter web bundle;
deployment was correctly skipped for the draft branch.

Closure requires: successful Pages and API deployment from the accepted change,
then an iPhone retest showing mileage edit plus at least one non-Part-Out
decision. Do not close this defect from CI evidence alone.

## Production Launch Preparation

### High

#### DEF-PROD-001: Production hosting, ingress, DNS, and TLS are not provisioned

Status: open, external blocker

Impact: Production traffic must remain closed.

Next action: Approve the production account and region, harden the host and
network, provision DNS and managed TLS, and retain external verification.

#### DEF-PROD-002: No approved image is published by immutable registry digest

Status: open, external blocker

Impact: The deployment cannot identify or retrieve an approved release artifact.

Next action: Configure the approved registry, publish the exact CI candidate,
record its SHA-256 digest and provenance, and create the release manifest.

#### DEF-PROD-003: Managed PostgreSQL recovery controls are not provisioned

Status: open, external blocker

Impact: Production data would lack evidenced encryption, point-in-time recovery,
retention, and target-environment restore capability.

Next action: Provision managed PostgreSQL, restrict network access, configure
encrypted backups and retention, approve RPO/RTO, and pass a restore drill.

#### DEF-PROD-004: Production secrets and IAM ownership are not approved

Status: open, external blocker

Impact: Database and first-owner credentials cannot be safely provisioned or rotated.

Next action: Configure the approved secret manager and deployment role, review
least privilege, assign rotation owners, and retain an access review.

#### DEF-PROD-005: Monitoring, incident response, and launch support are not active

Status: open, external blocker

Impact: Failures may not be detected, escalated, or rolled back within an approved window.

Next action: Route logs, metrics, uptime and readiness alerts; test delivery; and
assign on-call, incident command, rollback, and customer support ownership.

### Medium

#### DEF-PROD-006: Capacity, privacy, retention, and business launch approvals are absent

Status: open, external blocker

Impact: Technical repository readiness alone cannot authorize production use.

Next action: Approve target load and retention, complete privacy and terms review,
and record the accountable business go/no-go decision.

#### DEF-PROD-007: Production container gate awaits GitHub Actions evidence

Status: closed by CI evidence

Impact: None remaining for repository-level production preparation.

Resolution: Push run `29372078034` and pull-request run `29372080469` passed all
eight jobs at `847a1bed5e9a438d3a85758954abdca1400525a6`. The production
job validated Compose, image metadata, dependency integrity, clean migrations,
owner bootstrap, two workers, readiness, release identity, headers, hidden docs,
and login.

## Production Environment Provisioning

### High

#### DEF-ENV-001: Cloud provider and production account decision is unapproved

Status: open, external blocker

Evidence: No provider, account, region, budget, billing owner, or production
domain is recorded. The environment example intentionally contains placeholders.

Impact: Provider-specific infrastructure and billable resources must not be created.

Next action: Select the provider and service mapping, approve expected cost and
region, assign account ownership, and complete the credential-free contract.

#### DEF-ENV-002: Protected production environment and live acceptance are absent

Status: open, external blocker

Evidence: The manual GitHub workflow exists, but the `production` environment,
required reviewers, database secret, public endpoint, and managed database have
not been configured.

The database acceptance job also requires a protected self-hosted runner labelled
`recycleros-production` inside the private database network and the dedicated
`PRODUCTION_DATABASE_VERIFY_URL` environment secret.

Impact: Repository tests cannot prove target-environment TLS, IAM, recovery,
observability, or deployed release identity.

Next action: Provision the approved target, configure GitHub environment
protection, and pass `production-environment-acceptance.yml` with retained output.

### Medium

#### DEF-ENV-003: Provider-specific infrastructure as code is intentionally deferred

Status: open, blocked by provider decision

Evidence: A provider-neutral acceptance boundary is implemented; no AWS, Azure,
Google Cloud, or other provider has authority to become the production baseline.

Impact: Production resources are not reproducible from provider-specific IaC yet.

Next action: After DEF-ENV-001 closes, implement the selected provider module
against the committed contract without changing application behavior.
