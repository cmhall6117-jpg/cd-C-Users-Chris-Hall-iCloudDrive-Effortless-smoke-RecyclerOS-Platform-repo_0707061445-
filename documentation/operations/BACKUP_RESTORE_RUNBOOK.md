# Backup and Restore Runbook

## Policy Candidate

- proposed recovery point objective: 24 hours
- proposed recovery time objective: 4 hours
- daily custom-format PostgreSQL backup
- 14 daily and 8 weekly recovery points
- encrypted off-host copy after every successful backup
- restore rehearsal before pilot launch and at least quarterly

These targets require business approval and an assigned restore owner before a
data-bearing pilot begins.

## Create Backup

The PostgreSQL pilot port is bound to loopback. Set `DATABASE_URL` from the
secret file without placing the password in a command argument, then run:

```powershell
$postgresPassword = Get-Content -Raw deploy/pilot/secrets/postgres_password
$env:DATABASE_URL = "postgresql://recycleros:$postgresPassword@127.0.0.1:5432/recycleros_pilot"
python tools/scripts/pilot_postgres_backup.py --output build_artifacts/pilot_backups/recycleros-pilot.dump
Remove-Item Env:DATABASE_URL
$postgresPassword = $null
```

The tool creates a PostgreSQL custom-format dump and a JSON manifest containing
the SHA-256 digest, UTC creation time, database name, and size. It refuses to
overwrite an existing backup unless `--overwrite` is explicitly supplied.

Copy both files to the approved encrypted off-host destination. A backup is not
complete until the copy and checksum are verified.

## Restore Rehearsal

Create a new empty target database through the source admin connection:

```powershell
$env:RECYCLEROS_RESTORE_DATABASE_NAME = "recycleros_restore_drill"
python tools/scripts/pilot_postgres_create_database.py
```

Restore requires an exact target-name confirmation:

```powershell
$env:RECYCLEROS_RESTORE_DATABASE_URL = "postgresql://recycleros:$postgresPassword@127.0.0.1:5432/recycleros_restore_drill"
$env:RECYCLEROS_RESTORE_CONFIRM = "recycleros_restore_drill"
python tools/scripts/pilot_postgres_restore.py `
  --backup build_artifacts/pilot_backups/recycleros-pilot.dump `
  --manifest build_artifacts/pilot_backups/recycleros-pilot.dump.manifest.json
$env:RECYCLEROS_VERIFY_DATABASE_VARIABLE = "RECYCLEROS_RESTORE_DATABASE_URL"
python tools/scripts/pilot_postgres_verify.py --require-runtime-data
```

Record the backup manifest, restore start/end times, verification output, and
operator. Remove all temporary environment variables after the rehearsal.

## Railway Recovery Evidence

The August 9, 2026 Railway rehearsal created a PostgreSQL 16.14 custom archive,
matched its server and downloaded SHA-256 values, encrypted the off-platform
copy, and restored it into the clean target
`recycleros_restore_verify_a65d704f`. Verification found 24 public tables, 11
migration-ledger rows, and the expected organization, workspace, user, and
membership records. The temporary database was dropped, local plaintext and
SSH keys were removed, and Railway reported no registered SSH keys.

The retained encrypted artifact and DPAPI-protected recovery key are in the
iCloud-synced `private-backups` folder outside Git. The manifest is
`recycleros-pilot-2026-08-09-rc1.manifest.txt`. DPAPI protection is tied to the
current Windows account; cross-device key escrow remains mandatory before field
use.

Railway's CLI required a human for staging-file deletion. On August 9, 2026,
the operator ran this exact command:

```powershell
railway volume files delete --volume postgres-volume-gHwe /recycleros-pilot-2026-08-09-rc1.dump
```

Railway returned `Deleted /recycleros-pilot-2026-08-09-rc1.dump`. The operator
verified the file was absent, revoked the cleanup SSH key, removed its local key
files, and confirmed that Railway had no registered SSH keys.

This one-time drill does not satisfy the proposed daily cadence, retention
policy, native volume schedule, or restore-owner approval.

## Production Restore Controls

- stop writes before restore
- obtain explicit incident or change approval
- verify target database name twice
- preserve the failed database for investigation when storage permits
- restore to a new empty database whenever possible
- run schema, auth, opportunity, and inventory verification before switching traffic
- retain command output in the release or incident evidence record
- require the matching SHA-256 backup manifest before every production restore
