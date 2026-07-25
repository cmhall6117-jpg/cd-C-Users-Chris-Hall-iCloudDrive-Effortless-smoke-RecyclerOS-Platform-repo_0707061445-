# Add Cost-Bounded GCP Pilot Environment

## Summary

Adds the credential-free Google Cloud pilot candidate for project
`recyleros-platform` (`728951606960`) without creating cloud resources or
activating additional vertical slices.

## Changes

- adds separate Terraform bootstrap and repeatable environment roots
- caps Cloud Run at 1 vCPU, 1 GiB, minimum 0, and maximum 2 instances
- defines private PostgreSQL 16 Enterprise on single-zone `db-g1-small` with
  25 GiB storage, backups, point-in-time recovery, and deletion protection
- uses Secret Manager write-only values and GitHub Workload Identity Federation
  with no static service account keys
- adds protected manual infrastructure and release workflows
- adds a credential-free pilot contract, validator, focused tests, runbooks,
  defect updates, and release evidence
- adds Terraform validation to the RC1 integration workflow

## Why

This creates a controlled, reviewable path for one or two field testers while
preserving the separate production availability contract and keeping every
billable or public action behind explicit approval.

## Local Evidence

- Terraform 1.14.6 format check passed
- bootstrap and environment roots validated with Google provider 7.41.0 and
  Random provider 3.9.0
- backend: 59 passed and 2 PostgreSQL-only tests skipped
- Python compilation passed
- SQLite initialized through all 10 migrations and tenant checks
- workflow YAML parsed successfully
- staged credential signature scan passed

## Approval Boundary

No Google Cloud resources, credentials, secrets, images, or public endpoints
were created. Billing, budget alerts, bootstrap apply, protected GitHub
environment setup, monitoring delivery, and restore evidence remain external
blockers.
