# RC1 Build Report

## Repository

- Branch: `codex/rc1-backend-baseline`
- Monorepo root: `repo_0707061445`
- Source package archive: `archive/source_packages`
- Repository inventory: `documentation/repository/REPOSITORY_INVENTORY.md`

## Backend

- FastAPI entrypoint: `services/api/src/main.py`
- Registered routers: health, opportunities, vehicles, procurement, pick list, harvest, inventory
- Tenant context dependency: `services/api/src/tenant.py`
- Injectable storage dependency: `services/api/src/dependencies.py`
- RC1 process-local store: `services/api/src/store.py`
- Automated tests: `services/api/tests/test_tenant_isolation.py` and `services/api/tests/test_rc1_workflow.py`

Local result:

- Backend requirements are available in the ignored repository `.venv`.
- `python -m compileall services/api/src`: passed.
- FastAPI startup and OpenAPI route manifest check: passed with 10 paths.
- `pytest -q services/api/tests`: 13 passed in 7.39 seconds.
- PostgreSQL client dependencies were split into `services/api/requirements-postgres.txt` so backend tests and PostgreSQL migration checks can install only the dependencies they need in CI.

Inherited CI result:

- GitHub Actions `backend` passed on run `29289307269`.
- The backend job includes dependency install, `python -m compileall src`, and `pytest -q tests`.
- Current branch CI is pending its draft pull request.

## Flutter

- App routes registered in `apps/recycleros_pro_mobile/lib/src/app/app_routes.dart`
- Active path: login, workspace selection, mission control, opportunities, vehicle record, procurement, pick list, focus point, inventory intake

Local result:

- `flutter pub get`: blocked by local command timeout.
- `flutter analyze`: blocked by local command timeout.
- `flutter test`: blocked by local command timeout.

CI result:

- GitHub Actions `flutter` passed on run `29289307269`.
- The Flutter job includes `flutter pub get`, `flutter analyze`, and `flutter test`.

## CI

GitHub Actions workflow added at `.github/workflows/rc1-ci.yml` for backend, SQLite migrations, PostgreSQL migrations, and Flutter checks.

Latest PR workflow run `29289307269` passed all jobs:

- backend
- sqlite-migrations
- postgres-migrations
- flutter

## Pull Request

Draft pull request #1 remains open for repository integration.

Backend baseline PR text is available at `documentation/release/RC1_BACKEND_BASELINE_PR.md`.
