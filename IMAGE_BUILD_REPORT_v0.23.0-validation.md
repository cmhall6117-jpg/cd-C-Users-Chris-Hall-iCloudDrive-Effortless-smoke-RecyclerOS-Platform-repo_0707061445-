# RecyclerOS API image build report

- Image tag: `recycleros-api:0.23.0-validation`
- Archive: `recycleros-api_0.23.0-validation_docker-image.tar.gz`
- Architecture: `linux/amd64`
- Runtime user: `10001:10001`
- Runtime: Python 3.13.5 daemonless fallback
- Compressed bytes: 41395311
- SHA-256: `d277fa3e58151fe08f540a6a294c53a9a7ba24a7cc3ff0cb80cbfda582a3c81c`

## Executed validation

- Full service suite: 84 passed
- Non-root preflight: passed
- HTTP liveness: passed
- HTTP readiness: passed
- Metrics endpoint: passed
- Correlation response header: passed

## Source hotfixes found during image execution

1. Replaced the nonexistent preflight import `inspect_schema_state` with `ensure_schema_current`.
2. Replaced fixed parent-depth migration root lookup with upward migration-directory discovery.
3. Applied the same container-safe root discovery to observability migration checks.

## Limitation

The environment could not pull `python:3.11-slim` or install `psycopg[binary]`. This is therefore a runnable SQLite validation image, not the production promotion image. The source hotfix archive is suitable for the normal Docker/GitHub build path.
