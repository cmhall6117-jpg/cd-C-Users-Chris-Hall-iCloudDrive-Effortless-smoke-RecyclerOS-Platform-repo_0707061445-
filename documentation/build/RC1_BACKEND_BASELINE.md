# RC1 Backend Baseline

## Scope

Branch: `codex/rc1-backend-baseline`

Parent: `codex/rc1-database-consolidation`

The backend baseline turns the existing fixed-response FastAPI scaffold into a
connected, tenant-scoped RC1 workflow:

1. Create and list an opportunity.
2. Convert the opportunity into a vehicle record.
3. Retrieve procurement analysis for that opportunity.
4. Add the vehicle to the pick list.
5. Start and complete a focus-point harvest session.
6. Intake a harvested part into inventory.

## Implementation

- Added a FastAPI application factory with injectable storage.
- Added a process-local, thread-safe `InMemoryStore` implementation.
- Registered the missing `/v1/pick-list` router.
- Replaced fixed demo IDs and static listings with connected records.
- Moved request models out of route modules into shared schema modules.
- Enforced tenant context on every workflow endpoint.
- Returned `404` for cross-tenant resource lookup and linkage attempts to avoid
  disclosing records owned by another tenant.

## Local Evidence

```text
python -m compileall services/api/src
Result: passed

PYTHONPATH=services/api/src pytest -q services/api/tests
Result: 13 passed in 7.39s

FastAPI OpenAPI startup check
Result: passed; API version 0.2.0 and 10 paths registered
```

## Known Limitation

The active storage implementation is intentionally process-local. PostgreSQL
migrations are consolidated, but API repository wiring to PostgreSQL is not part
of this baseline and remains open work before a production deployment.
