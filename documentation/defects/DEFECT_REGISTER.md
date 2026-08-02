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

Next action: Provision the approved host, DNS, TLS reverse proxy, and certificate,
then record external verification evidence.

#### DEF-PILOT-002: Real pilot secrets are not provisioned

Status: open, external blocker

Evidence: The repository contains secret references and safe creation tooling,
but no live values or approved access record.

Impact: A real pilot environment cannot be started securely.

Next action: Provision secrets in the approved password manager or secret store,
restrict deployment access, and record rotation ownership.

#### DEF-PILOT-003: Off-host backup operations are not configured

Status: open, external blocker

Evidence: Backup and restore tooling exists, but no encrypted destination,
schedule, retention job, or restore owner is configured.

Impact: A data-bearing pilot would lack an evidenced recovery process.

Next action: Approve recovery targets, configure the encrypted off-host schedule,
assign the restore owner, and complete a host-level restore rehearsal.

### Medium

#### DEF-PILOT-004: Central logs and readiness alerts are not routed

Status: open, external blocker

Evidence: The API exposes liveness and readiness, but no external log collector,
monitor, or alert recipient is configured.

Impact: An unattended pilot failure may not reach an operator promptly.

Next action: Connect container logs and readiness probes to the approved
monitoring service and test alert delivery.

#### DEF-PILOT-005: Pilot container and recovery checks await CI

Status: closed by CI evidence

Evidence: Local Python checks pass. Push run `29369194654` and pull-request run
`29369197183` passed the hardened container and populated backup/restore jobs.

Impact: None remaining for repository-level pilot readiness.

Resolution: The Linux image reached real readiness with a read-only filesystem,
dropped capabilities, and no-new-privileges. The recovery rehearsal restored and
verified auth, opportunity, and inventory data.

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
