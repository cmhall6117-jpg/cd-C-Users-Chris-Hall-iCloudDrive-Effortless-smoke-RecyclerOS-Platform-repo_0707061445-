# GCP Pilot Environment

This Terraform root creates the cost-bounded RecyclerOS pilot:

- Artifact Registry in `us-east4`
- a dedicated VPC and `/26` Cloud Run subnet
- private service networking
- PostgreSQL 16 on a single-zone `db-g1-small` Cloud SQL instance
- a 25 GiB disk, backups, point-in-time recovery, and deletion protection
- Secret Manager entries generated through Terraform write-only values
- a dedicated Cloud Run runtime identity
- an optional Cloud Run API capped at two instances
- an optional public uptime check and delivery policy

The default input creates the foundation but does not create the Cloud Run
service or public access. Initialize with the bootstrap state bucket:

```powershell
terraform init `
  -backend-config="bucket=recyleros-platform-728951606960-tfstate" `
  -backend-config="prefix=pilot/environment"
terraform plan -var-file=terraform.tfvars
```

The protected release workflow supplies the immutable image digest and Git SHA.
It is the only supported path for enabling unauthenticated API access.

The database connection string uses a local Cloud SQL Unix socket. Its
`sslmode=disable` setting applies to that local socket; the Cloud SQL connection
from Cloud Run remains encrypted and authenticated by the platform.

Do not increment `operator_password_version` as a general rotation mechanism.
The bootstrap password is persisted as a hash by the application, so an operator
password change must happen through the application before the secret is updated.
