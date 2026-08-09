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
| Pre-provisioning no-go | Passed locally | Validator returned `field_ready: false`. |
| Focused automated tests | Passed locally | 10 tests. |
| Dynamic `PORT` healthcheck | Passed locally | Focused Dockerfile test. |
| Full RC1 CI | Passed | Push run `30723893531` and PR run `30724007217` passed all 10 jobs. |
| Railway account and budget controls | Passed live | Private Pro project, MFA/passkey, USD 20 warning and USD 30 hard limit verified; expected monthly minimum is USD 20. |
| Runtime, domain, and sealed variables | Passed live | Successful US East API/PostgreSQL deployments, public HTTPS API, private database, sealed operator credential, exact release identity. |
| Database backup and restore | Partially passed live | August 9 custom dump, checksum match, encrypted off-platform copy, clean restore, staging cleanup, live PITR, a 164 MB native snapshot, and daily/weekly native schedules passed. Off-platform cadence, key escrow, and owner approval remain under `DEF-RAILWAY-003`. |
| Monitoring and protected acceptance | Partially passed | GitHub environment and Wait for CI exist; uptime, alert delivery, support ownership, and field approval remain under `DEF-RAILWAY-004`. |
| Second unique tester identity | Blocked for tester two | `DEF-RAILWAY-005`. |

Passed Railway gates above have live command or endpoint evidence. The contract
remains `planned` and field access remains blocked while scheduled recovery,
monitoring, ownership, and approval controls are incomplete. Railway remains a
pilot choice and does not change the production-provider decision.

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

The native backup is 164 MB and completed at 12:34 EDT. Daily backups are
enabled every 24 hours with six-day retention, and weekly backups are enabled
every seven days with one-month retention. Automated off-platform cadence,
cross-device key escrow, and restore ownership are not approved. This evidence
does not change `field_ready: false`.
