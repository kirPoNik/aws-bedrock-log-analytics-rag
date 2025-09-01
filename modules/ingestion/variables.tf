# modules/ingestion/variables.tf

variable "pipeline_name" {
  description = "Name for the OpenSearch Ingestion pipeline."
  type        = string
}

variable "opensearch_collection_endpoint" {
  description = "The endpoint of the OpenSearch Serverless collection."
  type        = string
}

variable "opensearch_collection_name" {
  description = "The name of the OpenSearch Serverless collection."
  type        = string
}

variable "embedding_lambda_arn" {
  description = "The ARN of the Lambda function for generating embeddings."
  type        = string
}

variable "ingestion_role_arn" {
  description = "The ARN of the IAM role for the ingestion pipeline."
  type        = string
}

variable "tags" {
  description = "A map of tags to assign to the resources."
  type        = map(string)
  default     = {}
}
