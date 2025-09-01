output "opensearch_collection_endpoint" {
  description = "The endpoint of the OpenSearch Serverless collection"
  value       = module.opensearch.collection_endpoint
}

output "opensearch_dashboard_endpoint" {
  description = "The endpoint of the OpenSearch Dashboards endpoint"
  value       = module.opensearch.dashboard_endpoint
}

output "opensearch_collection_arn" {
  description = "The ARN of the OpenSearch Serverless collection"
  value       = module.opensearch.collection_arn
}

output "pipeline_ingestion_url" {
  description = "The ingestion URL for the pipeline"
  value       = module.ingestion.pipeline_ingestion_url
}

output "lambda_function_arn" {
  description = "The ARN of the embedding Lambda function"
  value       = module.lambda_chatapp.lambda_function_arn
}