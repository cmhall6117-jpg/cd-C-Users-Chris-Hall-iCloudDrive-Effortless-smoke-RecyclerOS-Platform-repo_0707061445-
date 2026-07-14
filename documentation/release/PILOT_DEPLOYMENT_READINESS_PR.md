# Pilot Deployment Readiness

## Summary

- add a non-root, read-only FastAPI pilot image with migration-first startup
- add a loopback-bound, secret-backed PostgreSQL and API compose stack
- add liveness, database/auth readiness, trusted-host, and secret-file controls
- add guarded PostgreSQL backup, restore, checksum, and verification tooling
- add CI gates for the real pilot container and a populated backup/restore rehearsal

## Scope

This operationalizes the existing RC1 path without activating new product
slices. Live SSO, payment, marketplace, shipping, and AI credentials remain
outside the pilot implementation.

## Local Evidence

- backend tests: 38 passed, 1 PostgreSQL-only test skipped
- OpenAPI startup: 16 paths
- Python compile checks: passed
- local SQLite initialization: retained from RC1
- Docker/container execution: pending GitHub Actions because Docker is unavailable locally

## Pilot No-Go Items

- external pilot host, DNS, and TLS
- real secret provisioning and access approval
- encrypted off-host backup scheduling
- centralized logs and alert routing
- named pilot support and rollback authority

The pull request remains a deployment-readiness candidate until automated pilot
jobs pass and the external no-go items are closed outside the repository.
