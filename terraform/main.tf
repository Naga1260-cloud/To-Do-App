# VPC
module "vpc" {
  source = "./modules/vpc"

  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
}

# Security Groups
module "security_groups" {
  source = "./modules/security_groups"

  project_name        = var.project_name
  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  allowed_cidr_blocks = var.allowed_cidr_blocks
}

# ECR Repositories (always created — shared by EC2 and EKS)
module "ecr" {
  source = "./modules/ecr"

  project_name = var.project_name
  environment  = var.environment
}

# RDS PostgreSQL
module "rds" {
  source = "./modules/rds"

  project_name       = var.project_name
  environment        = var.environment
  db_subnet_group    = module.vpc.db_subnet_group_name
  security_group_ids = [module.security_groups.rds_sg_id]
  db_instance_class  = var.db_instance_class
  db_name            = var.db_name
  db_username        = var.db_username
  db_password        = var.db_password
}

# EC2 Instances (optional)
module "ec2" {
  count  = var.deploy_ec2 ? 1 : 0
  source = "./modules/ec2"

  project_name          = var.project_name
  environment           = var.environment
  vpc_id                = module.vpc.vpc_id
  public_subnet_id      = module.vpc.public_subnet_ids[0]
  api_security_group_id = module.security_groups.api_sg_id
  web_security_group_id = module.security_groups.web_sg_id
  instance_type         = var.ec2_instance_type
  key_pair_name         = var.ec2_key_pair_name
  db_endpoint           = module.rds.endpoint
  db_name               = var.db_name
  db_username           = var.db_username
  db_password           = var.db_password
  ecr_api_url           = module.ecr.api_repository_url
  ecr_frontend_url      = module.ecr.frontend_repository_url
  aws_region            = var.aws_region
}

# EKS Cluster (optional)
module "eks" {
  count  = var.deploy_eks ? 1 : 0
  source = "./modules/eks"

  project_name           = var.project_name
  environment            = var.environment
  vpc_id                 = module.vpc.vpc_id
  private_subnet_ids     = module.vpc.private_subnet_ids
  node_security_group_id = module.security_groups.eks_node_sg_id
  node_instance_type     = var.eks_node_instance_type
  desired_nodes          = var.eks_desired_nodes
  min_nodes              = var.eks_min_nodes
  max_nodes              = var.eks_max_nodes
}

# Secrets Manager (DB credentials)
module "secrets_manager" {
  source = "./modules/secrets_manager"

  project_name = var.project_name
  environment  = var.environment
  db_username  = var.db_username
  db_password  = var.db_password
  db_host      = module.rds.endpoint
  db_name      = var.db_name
  enable_irsa  = var.deploy_eks
  oidc_provider_arn = var.deploy_eks ? module.eks[0].oidc_provider_arn : ""
  oidc_provider     = var.deploy_eks ? module.eks[0].oidc_provider : ""
}

# CloudFront CDN (optional — for EC2 deployments in prod)
module "cloudfront" {
  count  = var.deploy_cloudfront && var.deploy_ec2 ? 1 : 0
  source = "./modules/cloudfront"

  project_name       = var.project_name
  environment        = var.environment
  ec2_web_public_dns = module.ec2[0].web_ec2_public_dns
  origin_secret      = random_password.cloudfront_origin_secret[0].result
  enable_waf         = var.enable_waf

  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }
}

resource "random_password" "cloudfront_origin_secret" {
  count   = var.deploy_cloudfront && var.deploy_ec2 ? 1 : 0
  length  = 32
  special = false
}
