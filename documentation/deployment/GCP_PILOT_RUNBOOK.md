# Google Cloud Pilot Runbook

## Scope

This runbook covers a limited field pilot for one or two authorized testers. It
uses the existing RecyclerOS RC1 path and does not activate payment,
marketplace, SSO, shipping, or AI credentials.

The deployment is a pilot, not the production high-availability baseline.

## Architecture

- Cloud Run: 1 vCPU, 1 GiB memory, request-based billing, zero minimum instances,
  maximum two instances, concurrency 20
- Cloud SQL: PostgreSQL 16 Enterprise, `db-g1-small`, single zone, private IP
  only, 25 GiB SSD, deletion protection, backups, and point-in-time recovery
- Networking: dedicated VPC, `/26` Direct VPC egress subnet, private service
  networking, and a Cloud SQL Unix socket
- Secrets: Google Secret Manager with Terraform ephemeral and write-only values
- Images: regional Artifact Registry with immutable release digests
- Identity: GitHub OIDC Workload Identity Federation with no static cloud keys
- Monitoring: Cloud Logging, readiness uptime check, and a verified notification
  channel

## Deployment Sequence

1. Validate the credential-free pilot contract.
2. Verify billing and the USD 100 budget alerts.
3. Apply the one-time bootstrap.
4. Configure the protected GitHub environment.
5. Run the infrastructure workflow in `plan` mode.
6. Apply the foundation after review.
7. Create and verify a Monitoring notification channel.
8. Run the release workflow to publish an immutable image and enable field
   access.
9. Retrieve the generated operator password directly from Secret Manager and
   store it in the approved password manager.
10. Complete the smoke path and restore rehearsal.

## Smoke Path

Verify:

1. `/v1/health/live` reports alive.
2. `/v1/health/ready` reports workflow storage and auth ready.
3. Login succeeds for `operator@effortlesssmoke.com`.
4. Organization and workspace selection succeeds.
5. Mission Control loads.
6. Opportunity Discovery creates and opens an opportunity.
7. Vehicle Record, Procurement, Pick List, and Inventory Intake complete.
8. Missing or mismatched tenant context remains rejected.

Use only synthetic or explicitly authorized pilot data.

## Rollback

1. Pause intake and record the incident and release SHA.
2. Confirm a current Cloud SQL backup before changing the service.
3. Re-run the protected release workflow from the last approved Git commit.
4. Verify the previous digest, health endpoints, login, and tenant isolation.
5. Do not destroy or recreate Cloud SQL during an application rollback.

Database restore is a separate destructive operation. It requires an assigned
restore owner, a selected target, explicit approval, and post-restore
verification.

## Stop Spending

Cloud Run already scales to zero. To suspend the field endpoint, remove public
invocation through an approved Terraform change while retaining Cloud SQL and
its backups. Cloud SQL continues to incur charges until deliberately removed.
Deletion protection must not be disabled without a verified backup and explicit
data-destruction approval.
