# RC1 Build Report

## Repository

- Branch: `codex/rc1-flutter-baseline`
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

CI result:

- GitHub Actions `backend` passed on current-branch run `29323035764`.
- The backend job includes dependency install, `python -m compileall src`, and `pytest -q tests`.

## Flutter

- App routes registered in `apps/recycleros_pro_mobile/lib/src/app/app_routes.dart`
- Active path: login, workspace selection, mission control, opportunities, vehicle record, procurement, pick list, focus point, inventory intake
- Shared workflow state: `apps/recycleros_pro_mobile/lib/src/state/rc1_workflow.dart`
- Shared domain dependency: `packages/recycleros_domain`
- Full-path test: `apps/recycleros_pro_mobile/test/rc1_workflow_test.dart`

Local result:

- `where flutter`: no executable found.
- `where dart`: no executable found.
- `flutter pub get`, `flutter analyze`, and `flutter test`: blocked locally until an SDK is installed.

CI result:

- GitHub Actions `flutter` passed on current-branch run `29323035764`.
- The Flutter job includes `flutter pub get`, `flutter analyze`, and `flutter test`.

## CI

GitHub Actions workflow added at `.github/workflows/rc1-ci.yml` for backend, SQLite migrations, PostgreSQL migrations, and Flutter checks.

Flutter baseline workflow run `29323035764` passed all jobs:

- backend
- sqlite-migrations
- postgres-migrations
- flutter

## Pull Request

Draft pull request #4 is open against `codex/rc1-backend-baseline`.

Flutter baseline PR text is available at `documentation/release/RC1_FLUTTER_BASELINE_PR.md`.
