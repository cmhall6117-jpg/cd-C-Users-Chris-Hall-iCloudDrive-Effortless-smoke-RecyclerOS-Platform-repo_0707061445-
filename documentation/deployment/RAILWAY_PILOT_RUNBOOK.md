# Railway Pilot Runbook

## Start Of Session

1. Confirm the last GitHub `RC1 Integration Checks` run passed for the exact
   deployed commit.
2. Confirm Railway reports both `Postgres` and `recycleros-api` healthy.
3. Confirm the USD 20 alert and USD 30 hard limit remain active.
4. Check the most recent daily and weekly backup timestamps.
5. Open `/v1/health/live`, `/v1/health/ready`, and `/v1/health`; require `200`,
   ready dependencies, and the expected release SHA.
6. Log in as the assigned tester and complete the organization/workspace choice.
7. Use synthetic or approved pilot records only.

Every Railway API deployment must update
`deploy/railway/pilot/pilot.contract.json` `runtime.release_commit` to the exact
deployed 40-character SHA in the same reviewed release change. Run the Railway
Pilot Monitor immediately afterward and keep field access stopped until release
identity passes. Record the successful recovery run in `monitor_evidence`.

## Core Field Test

Exercise and record the existing path without activating another vertical slice:

1. Login.
2. Organization and workspace selection.
3. Mission Control.
4. Opportunity discovery.
5. Vehicle record.
6. Procurement.
7. Pick list and focus point.
8. Inventory intake.
9. Logout and verify the session is revoked.

For each failure, record the time, tester, release SHA, screen or endpoint, and
whether data was retried. Do not paste credentials or database URLs into defect
evidence.

Run the credential-safe automated API path with the sealed service variables:

```powershell
railway run --service recycleros-api --environment pilot --no-local -- `
  python tools/scripts/railway_field_smoke.py `
  --base-url https://recycleros-api-pilot.up.railway.app `
  --release-sha <exact-40-character-deployed-sha> `
  --output <sanitized-evidence-path>
```

The command creates clearly labeled synthetic records, logs out, verifies
session revocation, and never serializes the password or bearer token. This API
smoke complements but does not replace the manual Flutter device session.

## Operator Credential Recovery

Use this procedure when the sealed pilot password is unavailable or rotation is
required. A sealed Railway variable cannot be read back. Changing that variable
alone also cannot rotate an existing database credential.

1. Stop field activity. Confirm the API and PostgreSQL services are healthy,
   PITR is current, and the latest scheduled volume backup completed.
2. Create a unique password of at least 24 characters in the approved password
   manager. Keep that entry open, but do not place the password in chat, shell
   history, screenshots, source control, or command arguments.
3. Confirm the deployed API image contains
   `services/api/operator_password_rotate.py`.
4. Register a workstation SSH key with Railway when no approved key exists:

   ```powershell
   railway ssh keys add
   ```

5. From the linked repository directory, run the no-echo rotation command:

   ```powershell
   railway ssh --service recycleros-api --environment pilot -- `
     python services/api/operator_password_rotate.py `
     --confirm-email operator@effortlesssmoke.com
   ```

6. Enter the saved password twice at the private prompts. Require the command
   to report `PASS operator credential rotated`. The transaction replaces the
   PBKDF2 credential, revokes existing sessions, clears login lockouts, and
   records a password-rotation audit event without the password.
7. In Railway, open `pilot` -> `recycleros-api` -> **Variables**, edit the sealed
   `RECYCLEROS_LOCAL_OPERATOR_PASSWORD` value to the same saved password, and
   deploy the staged change. Do not unseal the variable.
8. Require liveness and readiness to return HTTP 200. Sign in once through the
   Flutter pilot, confirm the assigned organization and workspace, and close the
   session.
9. Record the deployment ID, rotation time, operator email, successful login,
   and number of revoked sessions. Do not record the password, its hash, the
   database URL, or an authorization token.
10. Remove the temporary Railway SSH key after verification when it is not an
    approved durable support key.

## Backup And Restore

Before the first field session and after any material test data change:

1. Confirm Railway's daily and weekly volume backups are current.
2. Schedule a maintenance window and temporarily enable the PostgreSQL TCP
   proxy only for the named restore owner.
3. Run `tools/scripts/pilot_postgres_backup.py` from the protected workstation
   with the database URL supplied through a temporary environment variable.
4. Retain the custom-format dump and SHA-256 manifest in the encrypted approved
   off-platform location.
5. Clear the local environment variable and disable the TCP proxy immediately.
6. Restore into a separate clean PostgreSQL 16 target and run
   `tools/scripts/pilot_postgres_verify.py --require-runtime-data`.
7. Record the non-secret rehearsal reference in the Railway pilot contract.

Repository-side encrypted off-platform automation is defined in
`tools/scripts/pilot_postgres_offsite_backup.py`; setup, retention, scheduler,
and recovery-key controls are in
`documentation/operations/BACKUP_RESTORE_RUNBOOK.md`. It remains inactive until
the owner approves a synced destination, a secure way to reach private Railway
PostgreSQL for each run, and cross-device `age` identity escrow. Do not enable a
persistent public database proxy for convenience.

Never test restore by overwriting the active pilot volume. Never wipe a Railway
volume to troubleshoot an application deployment.

## Incident Stop

1. Stop field activity and record the incident time.
2. Remove or disable the API public domain if exposure is suspected.
3. Revoke the operator session and rotate the operator credential when relevant.
4. Preserve Railway logs, the release SHA, and database backup evidence.
5. Roll back only the API deployment to the last approved commit.
6. Re-run liveness, readiness, release identity, login, and the complete core path.

Database restore is a separate approved action. Forward-only migrations mean an
application rollback must remain compatible with the current schema.

## Cost Stop

If the USD 20 alert fires, pause nonessential testing and identify API, database,
storage, and egress usage. If forecast usage can reach USD 30, stop the API and
field test before the hard limit suspends workloads. Confirm database and backup
state before resuming.

## End Of Session

1. Log out and confirm the public endpoint still reports the approved release.
2. Review API and PostgreSQL logs for errors and failed logins.
3. Record defects and any data corrections.
4. Confirm backup status after material changes.
5. Stop or sleep the API when no tester needs it; keep PostgreSQL recovery
   controls intact.
