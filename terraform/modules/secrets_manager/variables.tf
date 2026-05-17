variable "project_name" {
  description = "Project name used for naming resources"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "db_username" {
  description = "Database username"
  type        = string
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "db_host" {
  description = "Database host endpoint"
  type        = string
}

variable "db_name" {
  description = "Database name"
  type        = string
}

variable "enable_irsa" {
  description = "Whether to create IAM role for EKS service account (IRSA)"
  type        = bool
  default     = false
}

variable "oidc_provider_arn" {
  description = "ARN of the EKS OIDC provider (required when enable_irsa = true)"
  type        = string
  default     = ""
}

variable "oidc_provider" {
  description = "EKS OIDC provider URL without https:// (required when enable_irsa = true)"
  type        = string
  default     = ""
}
