# Production Environment Provisioning Contract

## Summary

- add a credential-free, provider-neutral production environment contract
- validate immutable release, HTTPS/network, managed database, recovery, IAM,
  observability, ownership, and approval requirements
- add read-only public endpoint and managed PostgreSQL acceptance probes
- add a manually approved GitHub production-environment acceptance workflow
- keep provider choice, billable resources, live credentials, and traffic external

## Scope

This phase does not provision cloud resources or deploy production. It converts
the remaining environment decisions into machine-checkable gates and gives the
future provider-specific implementation one stable acceptance boundary.

## Evidence

Local and CI evidence is recorded in
`PRODUCTION_ENVIRONMENT_EVIDENCE.md`. Live acceptance remains blocked until a
provider, account, region, domain, registry, database, secrets, observability,
owners, and approvals are configured.
