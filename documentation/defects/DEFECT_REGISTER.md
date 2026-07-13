# Defect Register

## Critical

### DEF-RC1-001: PostgreSQL migration gate blocked locally

Status: open

Evidence: `docker compose up -d postgres` failed because `docker` is not recognized as a command. Earlier `docker --version` and `psql --version` checks timed out.

Impact: PostgreSQL migrations have not been executed against a local clean database.

Next action: Run the `postgres-migrations` GitHub Actions job or install Docker/PostgreSQL locally.

### DEF-RC1-002: Backend dependency installation is not reproducible locally yet

Status: open

Evidence: `pip install -r services/api/requirements.txt` timed out after the `psycopg` pin was corrected.

Impact: FastAPI startup import and automated pytest execution could not be completed locally.

Next action: Re-run dependency installation on a stable network or in GitHub Actions. PostgreSQL-only dependency installation has been split into `services/api/requirements-postgres.txt` to reduce the backend test job surface.

## High

### DEF-RC1-003: Flutter SDK commands hang locally

Status: open

Evidence: `flutter pub get`, `flutter analyze`, and `flutter test` timed out without usable command output.

Impact: Flutter gates are blocked locally.

Next action: Run the Flutter GitHub Actions job or repair local Flutter/Dart command availability.

### DEF-RC1-004: Standard `python -m compileall` hangs locally

Status: open

Evidence: `python -m compileall services/api/src` emitted compile activity but did not exit before timeout. A previous backend syntax check passed before the environment degraded.

Impact: RC1 cannot mark the requested compile gate passed with clean command completion.

Next action: Re-run in CI after backend dependencies install.

## Medium

### DEF-RC1-006: Draft pull request cannot be opened without a GitHub remote

Status: open

Evidence: `git remote -v` returned no configured remotes for the new local monorepo. The GitHub repository full name is not available in the workspace.

Impact: The draft PR request cannot be completed from this local repository state.

Next action: Add a GitHub remote or provide the target `owner/repo`, then push `codex/rc1-repository-integration` and open a draft PR.

### DEF-RC1-005: Generated migration number gap is preserved

Status: accepted risk

Evidence: Active migrations go from `006` to `022`.

Impact: Numbering is non-contiguous, but no duplicate migration numbers are active.

Next action: Keep the manifest explicit and avoid renumbering generated historical packages.
