variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name used for naming resources"
  type        = string
  default     = "todo-app"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "tododb"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "todouser"
}

variable "db_password" {
  description = "PostgreSQL master password"
  type        = string
  sensitive   = true
}

variable "ec2_instance_type" {
  description = "EC2 instance type for API and Frontend"
  type        = string
  default     = "t3.micro"
}

variable "ec2_key_pair_name" {
  description = "EC2 Key Pair name for SSH access"
  type        = string
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the web frontend"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "eks_node_instance_type" {
  description = "EKS worker node instance type"
  type        = string
  default     = "t3.medium"
}

variable "eks_desired_nodes" {
  description = "Desired number of EKS worker nodes"
  type        = number
  default     = 2
}

variable "eks_min_nodes" {
  description = "Minimum number of EKS worker nodes"
  type        = number
  default     = 1
}

variable "eks_max_nodes" {
  description = "Maximum number of EKS worker nodes"
  type        = number
  default     = 4
}

variable "deploy_eks" {
  description = "Whether to deploy EKS cluster (set false for EC2-only deployment)"
  type        = bool
  default     = false
}

variable "deploy_ec2" {
  description = "Whether to deploy EC2 instances"
  type        = bool
  default     = true
}

variable "deploy_cloudfront" {
  description = "Whether to deploy CloudFront distribution in front of EC2"
  type        = bool
  default     = false
}

variable "enable_waf" {
  description = "Whether to enable WAF Web ACL with CloudFront"
  type        = bool
  default     = false
}
