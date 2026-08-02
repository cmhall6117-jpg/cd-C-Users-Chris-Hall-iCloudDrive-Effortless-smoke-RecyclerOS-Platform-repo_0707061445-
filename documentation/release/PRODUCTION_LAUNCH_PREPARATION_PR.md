# Production Launch Preparation

## Summary

- enforce exact hosts, HTTPS origins, hidden docs, security headers, and release identity
- separate production migration and first-owner provisioning from API startup
- add migration checksum ledger and checksum-verified restore
- add digest-pinned external-database production Compose configuration
- add immutable release manifest and forward-schema rollback process
- add a production container CI gate without enabling live credentials or services

## Scope

This prepares the existing RC1 working path for controlled production release.
It does not add vertical slices or implement live SSO, payment, marketplace,
shipping, or AI integrations.

## Evidence

Local evidence passed with 46 backend tests and 2 PostgreSQL-only skips. Push
run `29372078034` and pull-request run `29372080469` passed all eight jobs at
`847a1bed5e9a438d3a85758954abdca1400525a6`.

The pull request must remain draft while any external production launch gate is
blocked. Full evidence is recorded in `PRODUCTION_RELEASE_EVIDENCE.md`.
