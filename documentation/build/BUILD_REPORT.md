# RC1 Build Report

## Repository

- Branch: `codex/rc1-core-working-path`
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
- FastAPI startup and OpenAPI route manifest check: passed with 11 paths.
- `pytest -q services/api/tests`: 17 passed in 9.52 seconds on the final local run.
- PostgreSQL client dependencies were split into `services/api/requirements-postgres.txt` so backend tests and PostgreSQL migration checks can install only the dependencies they need in CI.

CI result:

- GitHub Actions `backend` passed on PR run `29325554779`.
- The backend job includes dependency install, `python -m compileall src`, and `pytest -q tests`.

## Flutter

- App routes registered in `apps/recycleros_pro_mobile/lib/src/app/app_routes.dart`
- Active path: login, workspace selection, mission control, opportunities, vehicle record, procurement, pick list, focus point, inventory intake
- Shared workflow state: `apps/recycleros_pro_mobile/lib/src/state/rc1_workflow.dart`
- Live transport: `apps/recycleros_pro_mobile/lib/src/data/dio_rc1_gateway.dart`
- Injected transport contract: `apps/recycleros_pro_mobile/lib/src/data/rc1_gateway.dart`
- Shared domain dependency: `packages/recycleros_domain`
- Full-path test: `apps/recycleros_pro_mobile/test/rc1_workflow_test.dart`

Local result:

- `where flutter`: no executable found.
- `where dart`: no executable found.
- `flutter pub get`, `flutter analyze`, and `flutter test`: blocked locally until an SDK is installed.

CI result:

- `flutter pub get`, `flutter analyze`, and `flutter test` passed on PR run
  `29325554779`.
- The live Dio-to-FastAPI core path passed in the `core-integration` job on the
  same run.

## CI

GitHub Actions workflow added at `.github/workflows/rc1-ci.yml` for backend, SQLite migrations, PostgreSQL migrations, and Flutter checks.

Core working path PR workflow run `29325554779` passed all jobs:

- backend
- sqlite-migrations
- postgres-migrations
- flutter
- core-integration

## Pull Request

Draft pull request #5 is open and mergeable against
`codex/rc1-flutter-baseline`:

`https://github.com/cmhall6117-jpg/cd-C-Users-Chris-Hall-iCloudDrive-Effortless-smoke-RecyclerOS-Platform-repo_0707061445-/pull/5`

Core working path PR text is available at
`documentation/release/RC1_CORE_WORKING_PATH_PR.md`.
