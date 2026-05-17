output "distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.web.id
}

output "domain_name" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.web.domain_name
}

output "hosted_zone_id" {
  description = "CloudFront hosted zone ID (for Route 53 alias records)"
  value       = aws_cloudfront_distribution.web.hosted_zone_id
}
