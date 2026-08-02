# RC1 Release Evidence

## Release Gate Status

| Gate | Status | Evidence |
| --- | --- | --- |
| Source packages archived | Passed | All discovered ZIP files copied to `archive/source_packages`. |
| Repository inventory | Passed | `documentation/repository/REPOSITORY_INVENTORY.md`. |
| FastAPI routers registered | Passed | `services/api/src/main.py`. |
| Valid FastAPI entrypoint | Passed | `backend` succeeded on auth pull-request run `29363414967`. |
| Authenticated sessions | Passed | Login, bearer, expiry, and identity tests passed on run `29363414967`. |
| Tenant membership enforcement | Passed | Membership and mismatch tests passed on run `29363414967`. |
| RBAC enforcement | Passed | Owner/admin/operator/viewer tests passed on run `29363414967`. |
| Tenant context enforcement | Passed | Authenticated tenant tests and live integration passed on run `29363414967`. |
| Flutter routes registered | Passed | `flutter` succeeded on run `29363414967`. |
| SQLite clean initialization | Passed | `build_artifacts/sqlite_init_report.txt`. |
| PostgreSQL clean migration | Passed | `postgres-migrations` succeeded on run `29363414967`. |
| Backend automated tests | Passed | 26 tests passed locally and `backend` succeeded on run `29363414967`. |
| Connected backend RC1 workflow | Passed | Backend workflow tests and live integration succeeded on run `29363414967`. |
| Cross-tenant resource isolation | Passed | Authenticated isolation tests succeeded on run `29363414967`. |
| Connected Flutter RC1 workflow | Passed | Authenticated `core-integration` succeeded on run `29363414967`. |
| Flutter bearer and tenant headers | Passed | Dio and live integration tests succeeded on run `29363414967`. |
| Durable identity and sessions | Blocked | Local auth is process-local; tracked as `DEF-RC1-010`. |
| Durable API persistence | Blocked | Default backend storage is process-local; tracked as `DEF-RC1-007`. |
| Flutter analyze/test | Passed | `flutter` succeeded on run `29363414967`. |
| GitHub Actions checks | Passed | Five required jobs succeeded on push run `29363344692` and PR run `29363414967`. |
| Composite release-evidence check | Passed | Push run `29363973050` and PR run `29364157746` passed at commit `28eab96b8ed1ec8f03b2d4ecda6e1fea1fe5da53`. |
| Draft pull request | Passed | PR #7 is open, draft, green, and mergeable. |
| Draft pull request body | Passed | `documentation/release/RC1_CICD_RELEASE_EVIDENCE_PR.md`. |

## CI Evidence

Latest successful CI/CD release-evidence workflow:

- Workflow: RC1 Integration Checks
- Pull-request run: `29364157746`
- Push run: `29363973050`
- Branch: `codex/rc1-cicd-release-evidence`
- Commit: `28eab96b8ed1ec8f03b2d4ecda6e1fea1fe5da53`
- PR: `#7`
- Result: success
- Jobs passed: backend, sqlite-migrations, postgres-migrations, flutter,
  core-integration, release-evidence

Draft pull request:

- URL: `https://github.com/cmhall6117-jpg/cd-C-Users-Chris-Hall-iCloudDrive-Effortless-smoke-RecyclerOS-Platform-repo_0707061445-/pull/7`
- State: open
- Draft: true
- Mergeable: true

## RC1 Decision

RC1 has reached its first reproducible core working path in GitHub Actions.
The auth/tenant/RBAC increment and the composite release-evidence check are
verified by successful push and pull-request runs against their exact code
commits.

This does not pass durable persistence or durable identity gates. PostgreSQL API
repository wiring and a production `AuthService` implementation remain required
before production release.
