variable "project_id" {
  description = "Google Cloud project ID."
  type        = string
}

variable "project_number" {
  description = "Numeric Google Cloud project number."
  type        = string

  validation {
    condition     = can(regex("^[0-9]{6,20}$", var.project_number))
    error_message = "project_number must contain only digits."
  }
}

variable "region" {
  description = "Approved pilot region."
  type        = string
  default     = "us-east4"

  validation {
    condition     = var.region == "us-east4"
    error_message = "The approved RecyclerOS pilot region is us-east4."
  }
}

variable "deploy_api" {
  description = "Create the Cloud Run service only after an API image is available."
  type        = bool
  default     = false
}

variable "allow_unauthenticated_api" {
  description = "Permit field devices to reach the API. Requires explicit protected-environment approval."
  type        = bool
  default     = false
}

variable "api_image" {
  description = "Artifact Registry image pinned by sha256 digest."
  type        = string
  default     = ""

  validation {
    condition = (
      !var.deploy_api ||
      can(regex("@sha256:[0-9a-f]{64}$", var.api_image))
    )
    error_message = "api_image must be pinned to a sha256 digest when deploy_api is true."
  }
}

variable "release_sha" {
  description = "Git commit SHA deployed to the pilot."
  type        = string
  default     = ""

  validation {
    condition     = !var.deploy_api || can(regex("^[0-9a-f]{40}$", var.release_sha))
    error_message = "release_sha must be a 40-character lowercase Git SHA when deploy_api is true."
  }
}

variable "cors_origins" {
  description = "Comma-separated approved browser origins. Mobile clients do not require CORS."
  type        = string
  default     = ""
}

variable "notification_channel_ids" {
  description = "Existing Cloud Monitoring notification channel resource names."
  type        = list(string)
  default     = []
}

variable "database_password_version" {
  description = "Increment only during an approved database password rotation."
  type        = number
  default     = 1

  validation {
    condition     = var.database_password_version >= 1
    error_message = "database_password_version must be at least 1."
  }
}

variable "operator_password_version" {
  description = "Initial local operator secret version. Rotation requires an application-level password change."
  type        = number
  default     = 1

  validation {
    condition     = var.operator_password_version == 1
    error_message = "Do not rotate the operator bootstrap secret through Terraform alone."
  }
}
