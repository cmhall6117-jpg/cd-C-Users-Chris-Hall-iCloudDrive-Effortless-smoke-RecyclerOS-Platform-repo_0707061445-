# RC1 Build Report

## Repository

- Branch: `codex/rc1-repository-integration`
- Monorepo root: `repo_0707061445`
- Source package archive: `archive/source_packages`
- Repository inventory: `documentation/repository/REPOSITORY_INVENTORY.md`

## Backend

- FastAPI entrypoint: `services/api/src/main.py`
- Registered routers: health, opportunities, vehicles, procurement, harvest, inventory
- Tenant context dependency: `services/api/src/tenant.py`
- Automated tenant tests added: `services/api/tests/test_tenant_isolation.py`

Local result:

- Backend dependency installation is blocked by local pip timeout.
- FastAPI startup and pytest are blocked until dependencies install.
- Standard compileall is currently blocked by local command timeout.
- PostgreSQL client dependencies were split into `services/api/requirements-postgres.txt` so backend tests and PostgreSQL migration checks can install only the dependencies they need in CI.

CI result:

- GitHub Actions `backend` passed on run `29289307269`.
- The backend job includes dependency install, `python -m compileall src`, and `pytest -q tests`.

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

Draft pull request #1 is open and mergeable.

Prepared PR text is available at `documentation/release/PULL_REQUEST_DRAFT.md`.
