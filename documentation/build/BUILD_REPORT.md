# RC1 Build Report

## Repository

- Branch: `codex/rc1-auth-tenant-rbac`
- Monorepo root: `repo_0707061445`
- Source package archive: `archive/source_packages`
- Repository inventory: `documentation/repository/REPOSITORY_INVENTORY.md`

## Backend

- FastAPI entrypoint: `services/api/src/main.py`
- Registered routers: health, auth, opportunities, vehicles, procurement, pick list, harvest, inventory
- Auth implementation and boundary: `services/api/src/auth.py`
- Authenticated tenant/RBAC dependency: `services/api/src/tenant.py`
- Injectable storage dependency: `services/api/src/dependencies.py`
- RC1 process-local store: `services/api/src/store.py`
- Automated tests include `test_auth_rbac.py`, `test_tenant_isolation.py`, and `test_rc1_workflow.py`

Local result:

- Backend requirements are available in the ignored repository `.venv`.
- `python -m compileall services/api/src`: passed.
- FastAPI startup and OpenAPI route manifest check: passed with 13 paths.
- `pytest -q services/api/tests`: 26 passed in 12.95 seconds on the current local run.
- PostgreSQL client dependencies were split into `services/api/requirements-postgres.txt` so backend tests and PostgreSQL migration checks can install only the dependencies they need in CI.

Current branch CI result:

- Pending publication of `codex/rc1-auth-tenant-rbac`.
- The previous core working path remains green on run `29325554779`.

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

Current branch CI result:

- Pending publication. GitHub Actions will run `flutter pub get`,
  `flutter analyze`, `flutter test`, and the authenticated live
  Dio-to-FastAPI path.

## CI

GitHub Actions workflow added at `.github/workflows/rc1-ci.yml` for backend, SQLite migrations, PostgreSQL migrations, and Flutter checks.

Core working path PR workflow run `29325554779` passed all jobs before this
auth/RBAC increment. Current-branch CI evidence is pending publication.

- backend
- sqlite-migrations
- postgres-migrations
- flutter
- core-integration

## Pull Request

Draft pull request #5 is the green base for this branch. The auth/tenant/RBAC
draft pull request is pending publication against `codex/rc1-core-working-path`.

`https://github.com/cmhall6117-jpg/cd-C-Users-Chris-Hall-iCloudDrive-Effortless-smoke-RecyclerOS-Platform-repo_0707061445-/pull/5`

Proposed auth/tenant/RBAC PR text is available at
`documentation/release/RC1_AUTH_TENANT_RBAC_PR.md`.
