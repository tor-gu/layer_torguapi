output "layer_version_arn" {
  value = aws_lambda_layer_version.layer.arn
}

output "version" {
  value = aws_lambda_layer_version.layer.version
}

output "description" {
  value = aws_lambda_layer_version.layer.description
}
