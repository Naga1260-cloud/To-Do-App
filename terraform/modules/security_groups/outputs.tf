output "web_sg_id"      { value = aws_security_group.web.id }
output "api_sg_id"      { value = aws_security_group.api.id }
output "rds_sg_id"      { value = aws_security_group.rds.id }
output "eks_node_sg_id" { value = aws_security_group.eks_node.id }
