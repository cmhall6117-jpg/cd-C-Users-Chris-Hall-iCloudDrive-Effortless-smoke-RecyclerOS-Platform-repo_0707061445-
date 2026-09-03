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

## Automated Encrypted Off-Platform Backup

Repository implementation is available but is not activated. The operator must
approve the destination, database connection method, recovery-key escrow, and
RPO/RTO before registering the schedule.

`tools/scripts/pilot_postgres_offsite_backup.py` performs the following guarded
sequence:

1. Reads a config file containing paths and retention policy, never a database
   password or private encryption key.
2. Requires the config, database URL secret file, staging directory, and
   destination to be outside the Git repository.
3. Creates the custom PostgreSQL dump, SHA-256 manifest, and tar bundle in a
   temporary staging directory.
4. Encrypts the bundle to one public `age` recipient before any backup payload
   reaches the synced destination.
5. Copies the ciphertext, verifies its SHA-256 value, and creates the JSON
   envelope last as the completed-backup marker.
6. Keeps the newest 14 daily recovery points plus one older point from each of
   eight additional ISO weeks. Only valid RecyclerOS artifact/envelope pairs
   are eligible for removal; unrelated and malformed files are left alone.
7. Removes the temporary dump, plaintext manifest, and tar bundle when the run
   succeeds or fails.

The config refuses a private `age` identity. Keep only the public recipient on
the backup workstation. Store the private identity in the approved password
manager and a separately controlled recovery location. Never store it in Git,
the synced backup folder, the task command, or chat.

Copy `deploy/pilot/offsite-backup.config.example.json` to a protected location
outside the repository. Use absolute paths. The database URL file contains a
secret and must be limited to the operator account. The destination must
already exist so a misspelled or unavailable sync path fails closed.
Use absolute executable paths for both `age` and PostgreSQL 16 `pg_dump` because
Windows scheduled tasks may not inherit the interactive shell's `PATH`.

Railway PostgreSQL has no public endpoint at rest. Do not leave a TCP proxy
enabled to support this task. Before activation, approve either private-source
execution or a bounded connection procedure that opens the source only for the
backup and closes it afterward. The current task runner does not create or
expose Railway networking.

Validate without connecting to PostgreSQL or writing a backup:

```powershell
python tools/scripts/pilot_postgres_offsite_backup.py `
  --config C:\RecyclerOS\private\offsite-backup.config.json `
  --validate-only
```

After source connectivity is approved, run one attended backup and confirm that
the destination contains only a `.tar.age` artifact and its
`.tar.age.envelope.json` file:

```powershell
python tools/scripts/pilot_postgres_offsite_backup.py `
  --config C:\RecyclerOS\private\offsite-backup.config.json
```

Register the daily Windows task only after that attended run passes. The script
requires an exact confirmation, validates the config first, refuses to replace
an existing task, and registers a limited task that runs only while the current
operator is signed in:

```powershell
& tools/scripts/register_pilot_offsite_backup_task.ps1 `
  -ConfigPath C:\RecyclerOS\private\offsite-backup.config.json `
  -PythonExecutable C:\Path\To\python.exe `
  -DailyAt 02:00 `
  -Confirm "REGISTER RECYCLEROS OFFSITE BACKUP"
```

Disable the automation without deleting backup artifacts:

```powershell
Unregister-ScheduledTask `
  -TaskName "RecyclerOS Pilot Off-Platform Backup" `
  -Confirm:$false
```

Activation evidence must include config validation, the first attended run,
the first scheduled run, remote sync confirmation, task history, an escrow
record that exposes no key material, and a clean-target restore from one of the
scheduled encrypted artifacts.

To rehearse restore, first verify the ciphertext SHA-256 against the envelope,
then decrypt the tar into a protected temporary directory using the escrowed
identity. Extract the dump and its manifest and follow the clean-target restore
steps below. Remove the decrypted tar, dump, and manifest after verification.

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

This one-time drill did not by itself satisfy the proposed daily cadence or
retention policy. Later Railway evidence establishes native daily and weekly
volume schedules plus restore ownership. Automated off-platform execution and
cross-device key escrow remain unverified.

## Production Restore Controls

- stop writes before restore
- obtain explicit incident or change approval
- verify target database name twice
- preserve the failed database for investigation when storage permits
- restore to a new empty database whenever possible
- run schema, auth, opportunity, and inventory verification before switching traffic
- retain command output in the release or incident evidence record
- require the matching SHA-256 backup manifest before every production restore
