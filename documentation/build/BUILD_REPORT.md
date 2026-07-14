# RC1 Build Report

## Repository

- Branch: `codex/pilot-deployment-readiness`
- Monorepo root: `repo_0707061445`
- Source package archive: `archive/source_packages`
- Repository inventory: `documentation/repository/REPOSITORY_INVENTORY.md`

## Backend

- FastAPI entrypoint: `services/api/src/main.py`
- Registered routers: health, auth, opportunities, vehicles, procurement, pick list, harvest, inventory
- Auth implementation and boundary: `services/api/src/auth.py`
- Authenticated tenant/RBAC dependency: `services/api/src/tenant.py`
- Injectable storage dependency: `services/api/src/dependencies.py`
- Workflow store contract and local implementation: `services/api/src/store.py`
- PostgreSQL workflow implementation: `services/api/src/postgres_store.py`
- PostgreSQL auth implementation: `services/api/src/postgres_auth.py`
- Durable runtime migration: `database/migrations/postgres/026_rc1_durable_runtime.sql`
- Automated tests include `test_auth_rbac.py`, `test_tenant_isolation.py`, `test_rc1_workflow.py`, and `test_postgres_runtime.py`

Local result:

- Backend requirements are available in the ignored repository `.venv`.
- `python -m compileall services/api/src`: passed.
- FastAPI startup and OpenAPI route manifest check: passed with 14 paths.
- `pytest -q services/api/tests`: 28 passed and 1 PostgreSQL-only test skipped in 14.00 seconds on the current local run.
- SQLite clean initialization: passed all 10 client migrations, tenant-column checks, and tenant mismatch rejection.
- PostgreSQL restart test: passed in GitHub Actions against clean PostgreSQL 16 services.
- PostgreSQL client dependencies were split into `services/api/requirements-postgres.txt` so backend tests and PostgreSQL migration checks can install only the dependencies they need in CI.

Auth/tenant/RBAC baseline CI result:

- Pull-request run `29363414967` passed `python -m compileall src` and the
  complete 26-test backend suite at commit
  `9bf4490f91b914b05963208355218a863b632977`.

## Flutter

- App routes registered in `apps/recycleros_pro_mobile/lib/src/app/app_routes.dart`
- Active path: login, workspace selection, mission control, opportunities, vehicle record, procurement, pick list, focus point, inventory intake
- Shared workflow state: `apps/recycleros_pro_mobile/lib/src/state/rc1_workflow.dart`
- Live transport and bearer-session owner: `apps/recycleros_pro_mobile/lib/src/data/dio_rc1_gateway.dart`
- Injected transport contract: `apps/recycleros_pro_mobile/lib/src/data/rc1_gateway.dart`
- Shared domain dependency: `packages/recycleros_domain`
- Full-path test: `apps/recycleros_pro_mobile/test/rc1_workflow_test.dart`
- Auth/RBAC UI test: `apps/recycleros_pro_mobile/test/auth_rbac_ui_test.dart`

Local result:

- `where flutter`: no executable found.
- `where dart`: no executable found.
- `flutter pub get`, `flutter analyze`, and `flutter test`: blocked locally until an SDK is installed.

Auth/tenant/RBAC baseline CI result:

- Pull-request run `29363414967` passed `flutter pub get`, `flutter analyze`,
  `flutter test`, and the authenticated live Dio-to-FastAPI path.

## CI

GitHub Actions workflow at `.github/workflows/rc1-ci.yml` runs backend, SQLite,
PostgreSQL, Flutter, and authenticated core-integration checks. This branch adds
a final `release-evidence` job that summarizes the exact run, commit, event, and
prerequisite results, then fails unless all five required jobs passed.

The defect-closure candidate upgrades official checkout and Python setup actions
to their Node 24 major versions. The PostgreSQL job now applies migration `026`
and verifies the complete workflow, session persistence, logout revocation,
login throttling, and auth audit records across three app instances.

Defect-closure push run `29366652838` and pull-request run `29366685297`
passed all six jobs at commit
`7beea835073e42e8f07b90afbf1c4687e972d734`. Both runs used
`actions/checkout@v6` and `actions/setup-python@v6` with zero check annotations.

Auth/tenant/RBAC pull-request run `29363414967` passed all five prerequisite
jobs at commit `9bf4490f91b914b05963208355218a863b632977`:

- backend
- sqlite-migrations
- postgres-migrations
- flutter
- core-integration

The composite gate passed on push run `29363973050` and pull-request run
`29364157746` at commit
`28eab96b8ed1ec8f03b2d4ecda6e1fea1fe5da53`.

## Pull Request

Draft pull request #8 is open against `codex/rc1-cicd-release-evidence`:

`https://github.com/cmhall6117-jpg/cd-C-Users-Chris-Hall-iCloudDrive-Effortless-smoke-RecyclerOS-Platform-repo_0707061445-/pull/8`

PR text is available at
`documentation/release/RC1_DEFECT_CLOSURE_PR.md`.

## Pilot Deployment Readiness

- API version: `0.5.0`
- OpenAPI paths: 16
- Pilot image: `services/api/Dockerfile`
- Pilot stack: `deploy/pilot/compose.yml`
- Startup: ordered PostgreSQL migrations, then Uvicorn
- Runtime: non-root image, read-only filesystem, dropped capabilities, no-new-privileges
- Configuration: mounted secret files and required production trusted hosts
- Health: independent liveness and storage/auth readiness probes
- Recovery: custom-format backup, SHA-256 manifest, guarded restore, data verification
- Local backend result: 38 passed and 1 PostgreSQL-only test skipped in 16.27 seconds
- Container, compose, and backup/restore execution: pending GitHub Actions

The pilot readiness draft pull request is pending publication from
`codex/pilot-deployment-readiness`.
