# RC1 Release Evidence

## Release Gate Status

| Gate | Status | Evidence |
| --- | --- | --- |
| Source packages archived | Passed | All discovered ZIP files copied to `archive/source_packages`. |
| Repository inventory | Passed | `documentation/repository/REPOSITORY_INVENTORY.md`. |
| FastAPI routers registered | Passed | `services/api/src/main.py`. |
| Valid FastAPI entrypoint | Blocked | Import/startup cannot run until backend dependencies install. |
| Tenant context enforcement | Implemented, test blocked | `services/api/src/tenant.py` and `services/api/tests/test_tenant_isolation.py`. |
| Flutter routes registered | Implemented, analysis blocked | `apps/recycleros_pro_mobile/lib/src/app/app_routes.dart`. |
| SQLite clean initialization | Passed | `build_artifacts/sqlite_init_report.txt`. |
| PostgreSQL clean migration | Blocked | Docker/PostgreSQL unavailable locally; CI job added. |
| Backend automated tests | Blocked | pip install timed out locally. |
| Flutter analyze/test | Blocked | Flutter commands timed out locally. |
| GitHub Actions checks | Implemented | `.github/workflows/rc1-ci.yml`. |
| Draft pull request | Blocked | No GitHub remote or repository full name is configured for this local monorepo. |
| Draft pull request body | Passed | `documentation/release/PULL_REQUEST_DRAFT.md`. |

## Gates Not Marked Passed

The following gates are intentionally not marked passed because there is no successful local command output:

- FastAPI startup import
- backend pytest
- `python -m compileall src`
- PostgreSQL clean migration execution
- `flutter pub get`
- `flutter analyze`
- `flutter test`
- draft pull request creation

## RC1 Decision

RC1 is not releasable yet. It has reached an integrated source state with SQLite migration evidence, tenant enforcement code, and CI definitions, but the reproducible build gates are blocked by local tooling and dependency installation issues.
