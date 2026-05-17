variable "project_name"       { type = string }
variable "environment"        { type = string }
variable "db_subnet_group"    { type = string }
variable "security_group_ids" { type = list(string) }
variable "db_instance_class"  { type = string }
variable "db_name"            { type = string }
variable "db_username"        { type = string }
variable "db_password" {
  type      = string
  sensitive = true
}
