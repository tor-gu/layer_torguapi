output "readonly_role_arn" {
  value = aws_iam_role.readonly.arn
}

output "deploy_role_arn" {
  value = aws_iam_role.deploy.arn
}
