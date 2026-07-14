# Defect Register

## Critical

### DEF-RC1-001: PostgreSQL migration gate blocked locally

Status: closed by CI evidence

Evidence: `docker compose up -d postgres` failed because `docker` is not recognized as a command. Earlier `docker --version` and `psql --version` checks timed out.

Impact: PostgreSQL migrations have not been executed against a local clean database.

Resolution: GitHub Actions `postgres-migrations` succeeded on run `29289307269`.

### DEF-RC1-002: Backend dependency installation is not reproducible locally yet

Status: closed by CI evidence

Evidence: `pip install -r services/api/requirements.txt` timed out after the `psycopg` pin was corrected.

Impact: FastAPI startup import and automated pytest execution could not be completed locally.

Resolution: GitHub Actions `backend` succeeded on run `29289307269`. PostgreSQL-only dependency installation remains split into `services/api/requirements-postgres.txt`.

## High

### DEF-RC1-003: Flutter SDK commands hang locally

Status: closed by CI evidence

Evidence: `flutter pub get`, `flutter analyze`, and `flutter test` timed out without usable command output.

Impact: Flutter gates are blocked locally.

Resolution: GitHub Actions `flutter` succeeded on run `29289307269`.

### DEF-RC1-004: Standard `python -m compileall` hangs locally

Status: closed by CI evidence

Evidence: `python -m compileall services/api/src` emitted compile activity but did not exit before timeout. A previous backend syntax check passed before the environment degraded.

Impact: RC1 cannot mark the requested compile gate passed with clean command completion.

Resolution: GitHub Actions `backend` succeeded on run `29289307269`, including `python -m compileall src`.

## Medium

### DEF-RC1-006: Draft pull request cannot be opened without a GitHub remote

Status: closed

Evidence: PR #1 is open as draft at `https://github.com/cmhall6117-jpg/cd-C-Users-Chris-Hall-iCloudDrive-Effortless-smoke-RecyclerOS-Platform-repo_0707061445-/pull/1`.

Impact: None remaining for draft PR creation.

Resolution: GitHub CLI confirmed PR #1 is open, draft, and targeting `main` from `codex/rc1-repository-integration`.

### DEF-RC1-005: Generated migration number gap is preserved

Status: accepted risk

Evidence: Active migrations go from `006` to `022`.

Impact: Numbering is non-contiguous, but no duplicate migration numbers are active.

Next action: Keep the manifest explicit and avoid renumbering generated historical packages.
