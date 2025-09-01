variable "collection_arn" {
  description = "ARN of the OpenSearch Serverless collection."
  type        = string
}

variable "pipeline_name" {
  description = "Name of the OpenSearch Ingestion pipeline."
  type        = string
}

variable "lambda_function_name" {
  description = "Name of the embedding Lambda function."
  type        = string
}

variable "aws_region" {
  description = "The AWS region where resources are deployed."
  type        = string
}

variable "aws_account_id" {
  description = "The AWS account ID."
  type        = string
}

variable "lambda_bedrock_model_id" {
  description = "Bedrock model ID for embedding generation."
  type        = string
}
