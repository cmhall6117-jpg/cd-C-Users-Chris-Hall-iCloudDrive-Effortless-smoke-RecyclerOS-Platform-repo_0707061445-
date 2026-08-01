# Railway Pilot Environment Pull Request

## Summary

Adds a budget-gated Railway pilot option for the existing RecyclerOS RC1 path.
The change does not create resources, store credentials, or activate another
vertical slice.

## Changes

- adds Railway Dockerfile configuration for one US East API replica with a
  512 MiB memory limit, one CPU limit, serverless sleep, and readiness healthcheck
- uses Railway private service references for PostgreSQL and the public domain
- makes the image healthcheck honor Railway's assigned `PORT`
- adds a credential-free pilot contract and validator with strict no-go gates
- adds focused contract tests and RC1 CI enforcement
- adds a protected, read-only manual endpoint acceptance workflow
- documents setup, recovery, field testing, cost response, and open defects

## Local Evidence

- Railway contract validation: passed; planned contract correctly reports
  `field_ready: false`
- Railway official JSON schema validation: passed
- focused Railway tests: 9 passed
- Python compile check: passed
- full backend: 63 passed and 2 PostgreSQL-only tests skipped
- SQLite clean initialization and workflow YAML parsing: passed
- GitHub checks: pending exact-head evidence

## External Blockers

- Railway account, Hobby billing, project, and cost controls are not approved
- API, PostgreSQL, public domain, sealed operator secret, and monitoring do not exist
- native/off-platform backups and a restore rehearsal are not evidenced
- GitHub `railway-pilot` environment and field-access approval are not configured
- a second tester requires a separate durable identity

## Decision

Repository configuration is a candidate only. No field access is authorized
until the strict contract and manual Railway pilot acceptance workflow pass.
