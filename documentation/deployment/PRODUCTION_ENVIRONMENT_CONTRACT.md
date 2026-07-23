# Production Environment Contract

## Purpose

`deploy/production/environment.example.json` is the credential-free contract for
the real RecyclerOS production environment. It records decisions and evidence,
not passwords, tokens, private keys, or database URLs.

The contract is safe to review and commit after every placeholder is replaced.
Live credentials remain in the approved secret manager and the protected GitHub
`production` environment.

## Required Decisions

The contract records:

- provider, account, and region
- exact image repository, SHA-256 digest, and Git commit
- public HTTPS API URL, browser origins, and trusted proxy networks
- private PostgreSQL 16+, TLS, encryption, deletion protection, and availability
- RPO, RTO, retention, point-in-time recovery, and restore rehearsal evidence
- registry, secret manager, deployment role, image signing, and IAM review
- log, metric, uptime, and alert destinations
- deployment, restore, incident, security, and business owners
- technical, security, and business approvals

Credential-like field names are rejected anywhere in the document. The database
must be private, browser origins must be exact HTTPS origins, and the release must
use complete immutable identifiers.

## Validation Modes

The checked-in example may be validated structurally:

```powershell
python tools/scripts/production_environment_contract.py `
  --contract deploy/production/environment.example.json `
  --allow-placeholders
```

For a real environment, create `deploy/production/environment.json`, replace all
placeholders, set `lifecycle` to `verified`, and run:

```powershell
python tools/scripts/production_environment_contract.py `
  --contract deploy/production/environment.json `
  --require-ready
```

Strict readiness also requires least-privilege review, image signing, and all
three approval fields. A valid contract does not itself deploy or authorize
traffic; it is one required input to the live acceptance workflow.
