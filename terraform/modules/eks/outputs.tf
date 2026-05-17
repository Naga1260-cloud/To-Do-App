output "cluster_name"     { value = aws_eks_cluster.main.name }
output "cluster_endpoint" { value = aws_eks_cluster.main.endpoint }
output "cluster_arn"      { value = aws_eks_cluster.main.arn }
output "node_group_arn"   { value = aws_eks_node_group.main.arn }
output "oidc_provider_arn" {
  value = aws_iam_openid_connect_provider.eks_oidc_provider.arn
}
output "oidc_provider" {
  value = replace(aws_eks_cluster.main.identity[0].oidc[0].issuer, "https://", "")
}
