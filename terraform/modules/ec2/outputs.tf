output "api_public_ip"       { value = aws_instance.api.public_ip }
output "api_private_ip"      { value = aws_instance.api.private_ip }
output "web_public_ip"       { value = aws_instance.web.public_ip }
output "web_private_ip"      { value = aws_instance.web.private_ip }
output "web_ec2_public_dns"  { value = aws_instance.web.public_dns }
