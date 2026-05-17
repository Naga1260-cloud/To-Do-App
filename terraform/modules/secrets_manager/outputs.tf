output "secret_arn" {
  description = "ARN of the DB credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.arn
}

output "secret_name" {
  description = "Name of the DB credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.name
}

output "api_role_arn" {
  description = "ARN of the IAM role for the API service account (IRSA)"
  value       = var.enable_irsa ? aws_iam_role.api_sa_role[0].arn : ""
}
