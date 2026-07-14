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

Local and GitHub evidence will be recorded in
`PRODUCTION_RELEASE_EVIDENCE.md`. The pull request must remain draft while any
external production launch gate is blocked.
