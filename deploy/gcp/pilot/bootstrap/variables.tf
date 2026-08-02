variable "project_id" {
  description = "Google Cloud project ID for the RecyclerOS pilot."
  type        = string
}

variable "project_number" {
  description = "Numeric Google Cloud project number used in Workload Identity Federation names."
  type        = string

  validation {
    condition     = can(regex("^[0-9]{6,20}$", var.project_number))
    error_message = "project_number must contain only digits."
  }
}

variable "state_bucket_name" {
  description = "Globally unique Cloud Storage bucket name for Terraform state."
  type        = string
}

variable "state_bucket_location" {
  description = "Cloud Storage location for Terraform state."
  type        = string
  default     = "US"
}

variable "github_repository" {
  description = "GitHub repository in owner/name form."
  type        = string
}

variable "github_deploy_ref" {
  description = "Only this exact Git ref may impersonate the pilot deployer."
  type        = string
  default     = "refs/heads/codex/gcp-pilot-environment"
}

variable "workload_identity_pool_id" {
  description = "Project-level Workload Identity Pool ID."
  type        = string
  default     = "github-recycleros-pilot"
}

variable "workload_identity_provider_id" {
  description = "GitHub OIDC provider ID within the pool."
  type        = string
  default     = "github"
}

variable "deployer_service_account_id" {
  description = "Service account ID used by approved GitHub Actions deployments."
  type        = string
  default     = "recycleros-pilot-deployer"
}
