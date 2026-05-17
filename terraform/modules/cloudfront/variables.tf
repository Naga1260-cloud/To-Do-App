variable "project_name" {
  description = "Project name used for naming resources"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "ec2_web_public_dns" {
  description = "Public DNS name of the EC2 web frontend instance"
  type        = string
}

variable "origin_secret" {
  description = "Secret header value to validate requests come from CloudFront (set on EC2 to reject direct access)"
  type        = string
  sensitive   = true
}

variable "acm_certificate_arn" {
  description = "ARN of ACM certificate (must be in us-east-1). Leave empty to use CloudFront default cert."
  type        = string
  default     = ""
}

variable "price_class" {
  description = "CloudFront price class (PriceClass_100=US/EU, PriceClass_200=+Asia, PriceClass_All=worldwide)"
  type        = string
  default     = "PriceClass_100"
}

variable "enable_waf" {
  description = "Whether to create a WAF Web ACL with rate limiting"
  type        = bool
  default     = false
}
