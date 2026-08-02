# RC1 Release Evidence

## Release Gate Status

| Gate | Status | Evidence |
| --- | --- | --- |
| Source packages archived | Passed | All discovered ZIP files copied to `archive/source_packages`. |
| Repository inventory | Passed | `documentation/repository/REPOSITORY_INVENTORY.md`. |
| FastAPI routers registered | Passed | `services/api/src/main.py`. |
| Valid FastAPI entrypoint | Passed | GitHub Actions `backend` job succeeded on core working path run `29325554779`. |
| Tenant context enforcement | Passed | Backend and live integration jobs succeeded on run `29325554779`. |
| Flutter routes registered | Passed | GitHub Actions `flutter` job succeeded on run `29325554779`. |
| SQLite clean initialization | Passed | `build_artifacts/sqlite_init_report.txt`. |
| PostgreSQL clean migration | Passed | GitHub Actions `postgres-migrations` job succeeded on run `29325554779`. |
| Backend automated tests | Passed | GitHub Actions `backend` job succeeded on run `29325554779`; 17 tests passed locally. |
| Connected backend RC1 workflow | Passed locally | `services/api/tests/test_rc1_workflow.py`; full backend suite reported 17 passed. |
| Cross-tenant resource isolation | Passed | Local tests and run `29325554779`; cross-tenant reads, links, and availability updates are rejected. |
| Connected Flutter RC1 workflow | Passed | `core-integration` started FastAPI and completed the live Dio path on run `29325554779`. |
| Flutter tenant headers | Passed | Dio mapping test and tenant-enforcing live API path passed on run `29325554779`. |
| Durable API persistence | Blocked | Default backend storage is process-local; tracked as `DEF-RC1-007`. |
| Flutter analyze/test | Passed | GitHub Actions `flutter` job succeeded on run `29325554779`. |
| GitHub Actions checks | Passed | Backend, SQLite, PostgreSQL, Flutter, and core integration jobs passed on run `29325554779`. |
| Draft pull request | Passed | PR #5 is open as draft and mergeable. |
| Draft pull request body | Passed | `documentation/release/RC1_CORE_WORKING_PATH_PR.md`. |

## CI Evidence

Latest successful code-evidence PR workflow:

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
Local workstation Flutter tooling remains unavailable, but the Flutter build,
tests, clean databases, and a live Dio-to-FastAPI smoke path have passing CI
evidence.

This does not pass the durable persistence gate. PostgreSQL API repository
wiring remains required before production release.
