# Add RC1 CI/CD Release Evidence Gate

## What Changed

- Added a final GitHub Actions `release-evidence` job after all five RC1 checks.
- Made the final job run even when a prerequisite fails so the summary always
  records every gate result.
- Added exact commit, branch, event, run URL, and gate results to the GitHub job
  summary.
- Updated build, smoke-test, defect, and release records with the successful
  auth/tenant/RBAC run IDs and commit.

## Why

The existing workflow produced five independent checks but no single auditable
release verdict. The new job consolidates them and fails unless every required
gate succeeded.

## Evidence

The auth baseline passed push run `29363344692` and pull-request run
`29363414967` at commit `9bf4490f91b914b05963208355218a863b632977`.
This branch must pass all six jobs before its release-evidence gate is promoted.

## Remaining Blocks

Durable API persistence and durable production identity remain blocked. This
change records evidence; it does not weaken or bypass those release gates.
