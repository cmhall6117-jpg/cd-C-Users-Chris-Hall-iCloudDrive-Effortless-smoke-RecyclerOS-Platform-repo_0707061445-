# RC1 Release Evidence

## Release Gate Status

| Gate | Status | Evidence |
| --- | --- | --- |
| Source packages archived | Passed | All discovered ZIP files copied to `archive/source_packages`. |
| Repository inventory | Passed | `documentation/repository/REPOSITORY_INVENTORY.md`. |
| FastAPI routers registered | Passed | `services/api/src/main.py`. |
| Valid FastAPI entrypoint | Passed | GitHub Actions `backend` job succeeded on core working path run `29325554779`. |
| Authenticated sessions | Pending CI | Local backend suite passed; current-branch CI evidence is pending publication. |
| Tenant membership enforcement | Pending CI | Local bearer, membership, and mismatch tests passed; current-branch CI is pending. |
| RBAC enforcement | Pending CI | Local owner/admin/operator/viewer matrix passed; current-branch CI is pending. |
| Tenant context enforcement | Pending CI | Local authenticated tenant tests passed; current-branch CI is pending. |
| Flutter routes registered | Passed | GitHub Actions `flutter` job succeeded on run `29325554779`. |
| SQLite clean initialization | Passed | `build_artifacts/sqlite_init_report.txt`. |
| PostgreSQL clean migration | Passed | GitHub Actions `postgres-migrations` job succeeded on run `29325554779`. |
| Backend automated tests | Pending CI | 26 tests passed locally in 12.95 seconds; current-branch CI is pending. |
| Connected backend RC1 workflow | Passed locally | `services/api/tests/test_rc1_workflow.py`; current local suite reported 26 passed. |
| Cross-tenant resource isolation | Passed locally | Current local tests reject cross-tenant reads, links, and availability updates; current-branch CI is pending. |
| Connected Flutter RC1 workflow | Pending CI | Authenticated live test is configured; current-branch CI is pending. |
| Flutter bearer and tenant headers | Pending CI | Dio test covers both; current-branch CI is pending. |
| Durable identity and sessions | Blocked | Local auth is process-local; tracked as `DEF-RC1-010`. |
| Durable API persistence | Blocked | Default backend storage is process-local; tracked as `DEF-RC1-007`. |
| Flutter analyze/test | Pending CI | Local Flutter SDK is unavailable; current-branch CI is pending. |
| GitHub Actions checks | Pending | Branch has not yet been published. |
| Draft pull request | Pending | Will target `codex/rc1-core-working-path`. |
| Draft pull request body | Passed | `documentation/release/RC1_AUTH_TENANT_RBAC_PR.md`. |

## CI Evidence

Latest successful base workflow:

- Workflow: RC1 Integration Checks
- Run: `29325554779`
- Branch: `codex/rc1-core-working-path`
- Commit: `80dbfc464a4e80e0590d1526863635abd1753235`
- PR: `#5`
- Result: success
- Jobs passed: backend, sqlite-migrations, postgres-migrations, flutter,
  core-integration

Draft pull request:

- URL: `https://github.com/cmhall6117-jpg/cd-C-Users-Chris-Hall-iCloudDrive-Effortless-smoke-RecyclerOS-Platform-repo_0707061445-/pull/5`
- State: open
- Draft: true
- Mergeable: true

## RC1 Decision

RC1 has reached its first reproducible core working path in GitHub Actions.
The auth/tenant/RBAC increment has local backend evidence but is not promoted to
passed until its exact branch head completes GitHub Actions.

This does not pass durable persistence or durable identity gates. PostgreSQL API
repository wiring and a production `AuthService` implementation remain required
before production release.
