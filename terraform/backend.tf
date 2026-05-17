terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }

  backend "s3" {
    bucket       = "todo-app-terraform-state-767900165633"
    key          = "todo-app/terraform.tfstate"
    region       = "us-east-1"              # must match the actual bucket region
    encrypt      = true
    use_lockfile = true                        # replaces deprecated dynamodb_table
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "todo-app"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# WAF for CloudFront must always be in us-east-1 (AWS requirement)
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"

  default_tags {
    tags = {
      Project     = "todo-app"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
