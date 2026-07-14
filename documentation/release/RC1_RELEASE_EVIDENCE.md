# RC1 Release Evidence

## Release Gate Status

| Gate | Status | Evidence |
| --- | --- | --- |
| Source packages archived | Passed | All discovered ZIP files copied to `archive/source_packages`. |
| Repository inventory | Passed | `documentation/repository/REPOSITORY_INVENTORY.md`. |
| FastAPI routers registered | Passed | `services/api/src/main.py`. |
| Valid FastAPI entrypoint | Passed | GitHub Actions `backend` job succeeded on backend baseline run `29320807780`. |
| Tenant context enforcement | Passed | GitHub Actions `backend` job succeeded on run `29320807780`; tests live in `services/api/tests/test_tenant_isolation.py`. |
| Flutter routes registered | Passed | GitHub Actions `flutter` job succeeded on Flutter baseline run `29323035764`. |
| SQLite clean initialization | Passed | `build_artifacts/sqlite_init_report.txt`. |
| PostgreSQL clean migration | Passed | GitHub Actions `postgres-migrations` job succeeded on run `29323035764`. |
| Backend automated tests | Passed | GitHub Actions `backend` job succeeded on run `29323035764`. |
| Connected backend RC1 workflow | Passed locally | `services/api/tests/test_rc1_workflow.py`; full backend suite reported 17 passed. |
| Cross-tenant resource isolation | Passed locally | `services/api/tests/test_tenant_isolation.py`; cross-tenant reads and link attempts return `404`. |
| Connected Flutter RC1 workflow | Pending | Live Dio gateway and injected fake path await current-branch CI. |
| Flutter tenant headers | Pending | Dio transport test awaits current-branch CI. |
| Durable API persistence | Blocked | Default backend storage is process-local; tracked as `DEF-RC1-007`. |
| Flutter analyze/test | Pending | Current-branch command evidence not yet available. |
| GitHub Actions checks | Pending | Core working path has not been pushed yet. |
| Draft pull request | Pending | Core working path draft PR not yet created. |
| Draft pull request body | Passed | `documentation/release/RC1_CORE_WORKING_PATH_PR.md`. |

## CI Evidence

Latest successful PR workflow:

- Workflow: RC1 Integration Checks
- Run: `29323035764`
- Branch: `codex/rc1-flutter-baseline`
- PR: `#4`
- Result: success
- Jobs passed: backend, sqlite-migrations, postgres-migrations, flutter

Draft pull request:

- URL: `https://github.com/cmhall6117-jpg/cd-C-Users-Chris-Hall-iCloudDrive-Effortless-smoke-RecyclerOS-Platform-repo_0707061445-/pull/4`
- State: open
- Draft: true
- Mergeable: true

## RC1 Decision

RC1 has reached the first reproducible build state in GitHub Actions. Local workstation tooling still has issues, but release gates that require command evidence now have passing CI evidence.

The backend baseline now provides a connected, locally verified RC1 workflow.
The Flutter baseline now provides the connected, CI-verified local user journey.
This does not pass the durable persistence gate; PostgreSQL API repository wiring
remains required before production release.
