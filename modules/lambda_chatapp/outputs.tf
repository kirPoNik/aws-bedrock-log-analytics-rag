# modules/lambda_chatapp/outputs.tf

output "lambda_function_arn" {
  description = "The ARN of the created Lambda function."
  value       = module.embedding_lambda.lambda_function_arn
}

output "lambda_function_name" {
  description = "The name of the created Lambda function."
  value       = module.embedding_lambda.lambda_function_name
}
