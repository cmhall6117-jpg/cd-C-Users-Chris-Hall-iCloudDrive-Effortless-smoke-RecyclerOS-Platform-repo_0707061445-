# RC1 Backend Baseline

## What Changed

- Replaced fixed FastAPI demo responses with tenant-scoped process-local state.
- Added an injectable application/store boundary for future PostgreSQL wiring.
- Added and registered the missing pick-list API router.
- Connected opportunity, vehicle, procurement, pick-list, focus-point, and
  inventory records through real generated identifiers.
- Added a complete RC1 workflow test and expanded tenant-isolation coverage.
- Added local API run and validation documentation.

## Why

The integrated scaffold compiled, but backend endpoints did not share state and
could return demo data for arbitrary tenant headers. This change establishes the
first testable backend behavior for the RC1 path while preserving the database
integration as an explicit next step.

## Developer Impact

Use `create_app()` to construct isolated API instances in tests. Routes receive
storage through a FastAPI dependency, so a PostgreSQL repository can replace the
current `InMemoryStore` without changing endpoint contracts.

## Validation

- `python -m compileall services/api/src`: passed.
- `pytest -q services/api/tests`: 13 passed.
- FastAPI startup/OpenAPI route check: passed with 10 registered paths.

## Known Limitation

Records reset on API restart. Durable PostgreSQL repository wiring is deferred
and tracked as `DEF-RC1-007`.
