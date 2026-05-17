variable "project_name"          { type = string }
variable "environment"           { type = string }
variable "vpc_id"                { type = string }
variable "public_subnet_id"      { type = string }
variable "api_security_group_id" { type = string }
variable "web_security_group_id" { type = string }
variable "instance_type"         { type = string }
variable "key_pair_name"         { type = string }
variable "db_endpoint"           { type = string }
variable "db_name"               { type = string }
variable "db_username"           { type = string }
variable "db_password" {
  type      = string
  sensitive = true
}
variable "ecr_api_url"      { type = string }
variable "ecr_frontend_url" { type = string }
variable "aws_region"       { type = string }
