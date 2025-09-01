output "opensearch_ingestion_role_arn" {
  description = "The ARN of the IAM role for the OpenSearch Ingestion pipeline."
  value       = aws_iam_role.osis_pipeline_role.arn
}

output "lambda_execution_role_arn" {
  description = "The ARN of the IAM role for the Lambda function."
  value       = aws_iam_role.lambda_execution_role.arn
}
