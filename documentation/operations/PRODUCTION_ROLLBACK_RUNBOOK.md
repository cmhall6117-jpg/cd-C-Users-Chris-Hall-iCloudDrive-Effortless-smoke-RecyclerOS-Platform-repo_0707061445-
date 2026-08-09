# Production Rollback Runbook

## Decision And Containment

1. Assign the incident commander and rollback operator.
2. Stop or drain intake when data consistency is at risk.
3. Record the current release SHA, image digest, health state, and database
   migration ledger.
4. Preserve logs and create a checksum-verified database backup.

## Application Rollback

Use this path when the database remains healthy and the previous application is
compatible with the forward schema.

1. Confirm the previous approved image digest and commit from its release
   manifest.
2. Confirm no migration requires a database downgrade.
3. Set `RECYCLEROS_API_IMAGE_DIGEST` and `RECYCLEROS_RELEASE_SHA` to that prior
   release.
4. Recreate the API service without deleting volumes or restoring data.
5. Verify liveness, readiness, release SHA, login, tenant scope, and the complete
   opportunity-to-inventory smoke path.
6. Keep traffic closed if any verification fails.

RecyclerOS migrations are forward-only. Application rollback must tolerate the
current schema; the migration ledger must never be edited to simulate downgrade.

## Database Recovery

Database restore is a separate destructive change. Prefer restoring the verified
backup into a new database, running `pilot_postgres_verify.py`, and switching the
database secret only after approval. Require the exact target-name confirmation
and backup manifest verification from the backup runbook.

Do not overwrite the failed database unless storage constraints and incident
approval are recorded. After switching, verify auth, tenant isolation, workflow
data, release SHA, and monitoring before reopening traffic.

## Evidence

Record the trigger, approvers, commands, backup and release manifests, old and
new image digests, database target, timestamps, validation output, customer
impact, and final disposition.
