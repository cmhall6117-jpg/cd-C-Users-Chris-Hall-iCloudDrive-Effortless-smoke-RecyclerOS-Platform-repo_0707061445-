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

## Railway Pilot Alternative

| Gate | Status | Evidence |
| --- | --- | --- |
| Railway config structure | Passed locally | Current official Railway JSON schema accepted `railway.json`. |
| Credential-free contract | Passed locally | Validator returned `valid: true`. |
| Pre-provisioning no-go | Passed locally | Validator returned `field_ready: false`. |
| Focused automated tests | Passed locally | 9 tests. |
| Dynamic `PORT` healthcheck | Passed locally | Focused Dockerfile test. |
| Full RC1 CI | Pending | Exact-head GitHub run has not completed. |
| Railway account and budget controls | Blocked external | `DEF-RAILWAY-001`. |
| Runtime, domain, and sealed variables | Blocked external | `DEF-RAILWAY-002`. |
| Database backup and restore | Blocked external | `DEF-RAILWAY-003`. |
| Monitoring and protected acceptance | Blocked external | `DEF-RAILWAY-004`. |
| Second unique tester identity | Blocked for tester two | `DEF-RAILWAY-005`. |

No Railway release gate is marked passed on the strength of configuration alone.
The provider-specific branch creates no resources and does not change the
production-provider decision.
