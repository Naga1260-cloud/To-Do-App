output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = module.rds.endpoint
}

output "rds_port" {
  description = "RDS port"
  value       = module.rds.port
}

output "ecr_api_url" {
  description = "ECR URL for the API image"
  value       = module.ecr.api_repository_url
}

output "ecr_frontend_url" {
  description = "ECR URL for the Frontend image"
  value       = module.ecr.frontend_repository_url
}

output "api_ec2_public_ip" {
  description = "Public IP of the API EC2 instance"
  value       = var.deploy_ec2 ? module.ec2[0].api_public_ip : null
}

output "web_ec2_public_ip" {
  description = "Public IP of the Web EC2 instance"
  value       = var.deploy_ec2 ? module.ec2[0].web_public_ip : null
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = var.deploy_eks ? module.eks[0].cluster_name : null
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = var.deploy_eks ? module.eks[0].cluster_endpoint : null
  sensitive   = true
}

output "connection_string" {
  description = "PostgreSQL connection string (without password)"
  value       = "postgresql://${var.db_username}:****@${module.rds.endpoint}:5432/${var.db_name}"
}
