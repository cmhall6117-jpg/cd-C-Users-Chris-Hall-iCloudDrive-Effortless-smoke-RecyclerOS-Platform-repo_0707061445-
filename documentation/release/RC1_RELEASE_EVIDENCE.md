# RC1 Release Evidence

## Release Gate Status

| Gate | Status | Evidence |
| --- | --- | --- |
| Source packages archived | Passed | All discovered ZIP files copied to `archive/source_packages`. |
| Repository inventory | Passed | `documentation/repository/REPOSITORY_INVENTORY.md`. |
| FastAPI routers registered | Passed | `services/api/src/main.py`. |
| Valid FastAPI entrypoint | Passed | `backend` succeeded on pull-request run `29366685297`. |
| Authenticated sessions | Passed | Login, bearer, expiry, and identity tests passed on run `29363414967`. |
| Tenant membership enforcement | Passed | Membership and mismatch tests passed on run `29363414967`. |
| RBAC enforcement | Passed | Owner/admin/operator/viewer tests passed on run `29363414967`. |
| Tenant context enforcement | Passed | Authenticated tenant tests and live integration passed on run `29363414967`. |
| Flutter routes registered | Passed | `flutter` succeeded on run `29363414967`. |
| SQLite clean initialization | Passed | Local check and `sqlite-migrations` run `29366685297`. |
| PostgreSQL clean migration | Passed | All 11 migrations succeeded on runs `29366652838` and `29366685297`. |
| Backend automated tests | Passed | 28 passed locally; backend and PostgreSQL tests passed on run `29366685297`. |
| Connected backend RC1 workflow | Passed | Backend workflow tests and live integration succeeded on run `29363414967`. |
| Cross-tenant resource isolation | Passed | Authenticated isolation tests succeeded on run `29363414967`. |
| Connected Flutter RC1 workflow | Passed | Authenticated `core-integration` succeeded on run `29363414967`. |
| Flutter bearer and tenant headers | Passed | Dio and live integration tests succeeded on run `29363414967`. |
| Durable identity and sessions | Passed | Session persistence and restart-safe revocation passed on run `29366685297`. |
| Durable API persistence | Passed | Complete workflow persistence across app/store restart passed on run `29366685297`. |
| Production fail-closed storage | Passed locally | Production startup without `DATABASE_URL` is rejected by an automated test. |
| Session revocation and login throttling | Passed | Durable logout, lockout, and audit tests passed on run `29366685297`. |
| Flutter analyze/test | Passed | `flutter` succeeded on run `29366685297`. |
| GitHub Actions checks | Passed | Six jobs succeeded on push run `29366652838` and PR run `29366685297`. |
| Composite release-evidence check | Passed | Both trigger paths passed at commit `7beea835073e42e8f07b90afbf1c4687e972d734`. |
| Draft pull request | Passed | PR #8 is open and draft. |
| Draft pull request body | Passed | `documentation/release/RC1_DEFECT_CLOSURE_PR.md`. |

## CI Evidence

Latest successful CI/CD release-evidence workflow:

- Workflow: RC1 Integration Checks
- Pull-request run: `29366685297`
- Push run: `29366652838`
- Branch: `codex/rc1-defect-closure`
- Commit: `7beea835073e42e8f07b90afbf1c4687e972d734`
- PR: `#8`
- Result: success
- Jobs passed: backend, sqlite-migrations, postgres-migrations, flutter,
  core-integration, release-evidence

Draft pull request:

- URL: `https://github.com/cmhall6117-jpg/cd-C-Users-Chris-Hall-iCloudDrive-Effortless-smoke-RecyclerOS-Platform-repo_0707061445-/pull/8`
- State: open
- Draft: true
- Mergeable: true

## RC1 Decision

RC1 has reached its first reproducible core working path in GitHub Actions.
The auth/tenant/RBAC increment and the composite release-evidence check are
verified by successful push and pull-request runs against their exact code
commits.

Durable persistence, durable identity, RC1 account controls, and supported
GitHub Action gates are passed by successful push and pull-request runs against
the exact implementation commit.

## Defect Closure Result

Branch `codex/rc1-defect-closure` adds the PostgreSQL workflow and auth
implementations, migration `026`, durable restart coverage, production
fail-closed selection, logout, login throttling, auth audit events, and Node 24
GitHub Action majors. Local evidence is 28 passed and 1 PostgreSQL-only test
skipped. GitHub then passed clean PostgreSQL restart coverage and every other
required job on both trigger paths with zero check annotations.

## Pilot Deployment Readiness

| Gate | Status | Evidence |
| --- | --- | --- |
| Secret-backed runtime configuration | Passed locally | Secret-file and conflict tests. |
| Production trusted-host enforcement | Passed locally | `test_pilot_runtime.py`. |
| Liveness and dependency readiness | Passed locally | 16-path startup and health tests. |
| Non-root read-only pilot image | Passed | Runs `29369194654` and `29369197183`. |
| Secret-backed compose validation | Passed | `docker compose config --quiet` in both runs. |
| Migration-first container startup | Passed | Real PostgreSQL/auth readiness in both runs. |
| Populated backup and clean restore | Passed | Auth and workflow data verified after restore. |
| Public DNS and TLS | Blocked external | `DEF-PILOT-001`. |
| Real secret provisioning | Blocked external | `DEF-PILOT-002`. |
| Off-host backup schedule | Blocked external | `DEF-PILOT-003`. |
| Central log and alert routing | Blocked external | `DEF-PILOT-004`. |

RC1 remains reproducible and green, and repository-level pilot deployment gates
passed at commit `59bd74a78c39923ad99d583a00f352a57d8dfb95`. Pilot launch
remains no-go until the external blockers have owner-approved evidence.

## Google Cloud Pilot Evidence

| Gate | Status | Evidence |
| --- | --- | --- |
| Project identity | Passed | `recyleros-platform`, `728951606960`. |
| Credential-free contract | Passed locally | Structural validator returned valid. |
| Cost and topology guardrail tests | Passed locally | 5 focused tests passed. |
| Terraform formatting and validation | Passed | `gcp-pilot-iac` succeeded on run `30162538935`. |
| Billing and USD 100 budget | Blocked external | Verification is absent. |
| Keyless GitHub trust | Blocked external | Bootstrap has not been applied. |
| Protected deployment approval | Blocked external | `gcp-pilot` environment is not evidenced. |
| Managed database and secrets | Blocked external | No infrastructure apply authorized. |
| Immutable API release | Blocked external | No image published or endpoint created. |
| Monitoring and restore evidence | Blocked external | Both remain pending. |

Decision: the repository and infrastructure-definition gates pass, but no live
Google Cloud environment gate passes and no field testing is authorized.

Repository reproducibility is passed at
`8b24fae4d540834edf0c041a9b06c8d619fa7058`: pull-request run
`30162538935` completed all 10 jobs successfully, including the composite
release-evidence gate. Live environment gates remain blocked because the run
validated definitions and application behavior but did not provision Google
Cloud resources.

## Railway Pilot Alternative

| Gate | Status | Evidence |
| --- | --- | --- |
| Railway config structure | Passed locally | Current official Railway JSON schema accepted `railway.json`. |
| Credential-free contract | Passed locally | Validator returned `valid: true`. |
| One-person field contract | Passed locally | Verified contract caps access at one tester and records project-owner approval. |
| Focused automated tests | Passed locally | 10 tests. |
| Dynamic `PORT` healthcheck | Passed locally | Focused Dockerfile test. |
| Full RC1 CI | Passed | Push run `32733071474` and PR run `32733139755` passed all 10 jobs for the verified one-person contract. |
| Railway account and budget controls | Passed live | Private Pro project, MFA/passkey, USD 20 warning and USD 30 hard limit verified; expected monthly minimum is USD 20. |
| Runtime, domain, and sealed variables | Passed live | Successful US East API/PostgreSQL deployments, public HTTPS API, private database, sealed operator credential, exact release identity. |
| Database backup and restore | Passed for one-person pilot | August 9 custom dump, checksum match, encrypted off-platform copy, clean restore, staging cleanup, live PITR, and restore-owner assignment passed. August 24 history proves daily and weekly native schedules produced real snapshots. Off-platform automation and key escrow remain broader-use hardening under `DEF-RAILWAY-003`. |
| Monitoring and protected acceptance | Passed for one-person pilot | Two-hour monitoring, simulated incident delivery and recovery, owner approval, and protected acceptance run `32770410381` passed. `DEF-RAILWAY-004` is closed. |
| Live tenant-scoped API working path | Passed for one-person pilot | Field run `20260824212230-5fd820be` passed 18 checks from login through inventory and revoked-session rejection. |
| Manual Flutter device working path | Partially passed | iPhone evidence now covers login, workspace selection, Mission Control, Opportunity Discovery, and synthetic opportunity `OPP-000002`; Vehicle Record through logout remains under `DEF-RAILWAY-006`. |
| Second unique tester identity | Blocked for tester two | `DEF-RAILWAY-005`. |

Passed Railway gates above have live command or endpoint evidence. The contract
is `verified`, limits access to one tester, and records explicit field approval
as `project-owner-approval-2026-08-24`. Protected acceptance passed for that
scope. Railway remains a pilot choice and does not change the
production-provider decision.

CI evidence applies to implementation commit
`fbf1c5f09c5a1d8c69a9f4ca312bf9a189e3fd8f` on draft pull request `#13`.
Both trigger paths passed backend, SQLite, PostgreSQL migration/replay and
restore, Flutter, live core integration, pilot and production containers,
production contract, Railway pilot config, and composite release evidence.

Live evidence applies to API deployment
`9ccd3586-b57f-4567-937f-0a6864d0d624`, PostgreSQL deployment
`9a092ef2-5f58-4cc8-92db-03f0af74b8d5`, and commit
`5784f4526e97de7cc60538d00ecc6977ca13a375`. Public health, release identity,
security headers, hidden docs, operator login/logout, valid tenant access, and
missing/mismatched tenant rejection passed on August 2, 2026.

Evidence-branch baseline `f3b732f5c75bc0c9088b1deefbd3f9149ac220a7`
passed all 22 checks on push run `31314925876` and pull-request run
`31315025909` for draft pull request `#15`.

Pull request `#15` merged to `main` on August 9, 2026, as commit
`e2b1fee3c83a03daf6aec31d5bf3e354133564b8`, activating the scheduled Railway
monitor. Healthy run `31331712419` passed. Simulated-failure run `31331739729`
failed as designed and opened issue `#16`. Recovery run `31331787276` passed
and closed issue `#16` as completed with a recovery comment. No Railway
resource was modified during this incident drill.

Recovery evidence applies to the live PostgreSQL service on August 9, 2026.
The source and downloaded custom archive shared SHA-256
`665035b1502c52ba4e80272073b1a8f5a2ee6d5bd4c22a1ff76bfe76a65d704f`.
The clean restore produced 24 public tables, 11 migration-ledger rows, and the
expected pilot organization, workspace, user, and membership. Encryption and
decryption verification reproduced the source hash. The temporary database and
local plaintext were removed. A human operator deleted and verified the
owner-only volume staging file, revoked the cleanup SSH key, removed its local
files, and confirmed that Railway reported no registered SSH keys.

The owner then upgraded the project to Pro and enabled PITR. PostgreSQL
deployment `ca3c8918-a664-4b6e-b9cc-998c0650ce27` repaired the WAL archive
credentials without replacing the database service or volume. Railway marked
the deployment active and successful at 12:44 EDT. The warning cleared, the
recovery window advanced from 12:35:54 through 13:19:18, and `/v1/health/ready`
returned HTTP 200 with storage and auth ready. Screenshot evidence:

- `documentation/release/evidence/railway/2026-08-09-postgres-deployment-ca3c8918.png`
  SHA-256 `fdbbb1c30d666ff24884b0a023181cf775dedd6cc11d087607bec07faef5cb36`
- `documentation/release/evidence/railway/2026-08-09-pitr-healthy.png`
  SHA-256 `c1926747c43373bfe8edc0f61cfec10ecde53a7ca121436cb7399daa31f8fab2`
- `documentation/release/evidence/railway/2026-08-09-volume-backup-1234.png`
  SHA-256 `43ae91d2d54d7fc027264aa04dd550c0875dd3e68d54119b1a62d1d7ee6c09a7`
- `documentation/release/evidence/railway/2026-08-09-volume-backup-schedule.png`
  SHA-256 `02cf2ad36545433cd6da3fa2f9cf855453f185aaee2770eae59c2f11627e5630`
- `documentation/release/evidence/railway/2026-08-24-scheduled-volume-backups.jpg`
  SHA-256 `39d270b2d85de6c5301209e7c43a5bbba85f32f7eb2bb95f21c352a695b82181`

The native backup is 164 MB and completed at 12:34 EDT. Daily backups are
enabled every 24 hours with six-day retention, and weekly backups are enabled
every seven days with one-month retention. On August 9, the project owner
assigned Chris Hall as both restore owner and support owner for the one-person
pilot. August 24 history shows completed daily snapshots of 485 MB and 472 MB,
a completed weekly snapshot of 470 MB, and the next run due in 14 hours.
Automated off-platform cadence and cross-device key escrow remain broader-use
hardening. On August 24, the project owner approved Chris Hall as the only field
tester. The verified contract records that approval and caps the environment at
one tester; a second tester remains blocked pending a separate durable identity.

PR `#19` merged the verified contract to `main` as commit
`e99fc294acffc69e078f134ab38344caf2d7401f`. Push run `32733071474` and
pull-request run `32733139755` passed all 10 RC1 jobs. Protected acceptance run
`32770410381` passed the contract, public-endpoint, and acceptance-evidence jobs.
The endpoint evidence recorded TLS 1.3 with 63 days remaining; HTTP 200 for
liveness, readiness, and exact release identity; all required security headers;
and HTTP 404 for docs and OpenAPI. The temporary `main` environment policy used
for the read-only run was removed, and only the original
`codex/railway-pilot-environment` policy remains.

One-person synthetic field run `20260824212230-5fd820be` exercised the live API
from login and tenant selection through Mission Control data, opportunity,
vehicle, procurement, pick list, Focus Point, inventory intake, logout, and
revoked-session rejection. All 18 checks passed. Missing tenant context returned
HTTP 400, mismatched context returned HTTP 403, and the revoked token returned
HTTP 401. The run created `OPP-000001`, `VEH-000001`, and `INV-000001` under
`org-local` / `workspace-local`. Sanitized evidence is retained at
`documentation/release/evidence/railway/2026-08-24-one-person-field-smoke.json`
with SHA-256
`7ceffa050ddba5a2901ac7794747b8882d105812536c10be24313a1888fc249f`.
No credential or token is present. Manual Flutter device interaction remains a
separate evidence gate under `DEF-RAILWAY-006`.

## Operator Credential Recovery Resolution

On August 26, 2026, loss of the password-manager copy of the sealed pilot
operator credential was recorded as `DEF-RAILWAY-007`. The recovery candidate
adds an explicit no-echo command that transactionally rotates the PostgreSQL
credential, revokes active sessions, clears login lockouts, and records a
non-secret audit event. Local compilation passed and the backend suite reported
78 passed with 3 PostgreSQL-only tests skipped. GitHub push run `32957902186`
and pull-request run `32957922930` passed all 11 RC1 jobs on both paths,
including clean PostgreSQL execution and pilot container packaging.

Before live rotation, the assigned tester recovered the original credential and
used it successfully on the iPhone pilot. PostgreSQL and the sealed Railway
variable remained synchronized and were not changed. The temporary recovery SSH
key was revoked and the temporary local key files were removed. The reviewed
rotation command remains available as a contingency, and `DEF-RAILWAY-007` is
closed without recording any secret in repository evidence.

## Partial iPhone UI Field Evidence

On August 26, 2026, Chris Hall used the public GitHub Pages Flutter pilot on an
iPhone to authenticate, render the Effortless Smoke, LLC organization and
RecyclerOS Operations workspace, select that workspace, and reach Mission
Control. The screen rendered tenant-scoped zero-state Opportunity, Pick List,
and Inventory metrics. No UI defect was observed in these stages.

The frontend is tied to successful workflow run `32783845146` at commit
`9c3814c07cab4d5c1c4301f8bf198aab5d310c36`. A read-only health check reported
the live Railway API at release
`e929c9977666b1fc30c7cdecbe30a2dfd3e4feef`, version `0.6.0`, with PostgreSQL
storage and auth. The screenshots, checksums, observed steps, and remaining
steps are retained in
`documentation/release/evidence/railway/2026-08-26-iphone-ui-manifest.json`.

On August 27, PR `#26` merged the browser-session route guard as commit
`d4e1da2fe6b6f5c29af9de95c2c444445744c69c`. Corrected CI run `33020582147`
passed all jobs, and GitHub Pages workflow run `33061203825` successfully built
and deployed the Flutter pilot. The public pilot endpoint returned HTTP 200.

Chris Hall then signed in again on the deployed build and created synthetic
opportunity `OPP-000002` with a blank VIN. The active-opportunity card and
enabled Create Vehicle Record action rendered. This closes `DEF-RAILWAY-008`
and further narrows `DEF-RAILWAY-006`. Manual iPhone evidence from Vehicle
Record through Inventory Intake and logout remains required before the
device-session gate can pass.
