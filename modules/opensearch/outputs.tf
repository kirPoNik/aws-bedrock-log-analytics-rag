output "collection_id" {
  description = "The ID of the OpenSearch Serverless collection."
  value       = aws_opensearchserverless_collection.vector_logs.id
}

output "collection_arn" {
  description = "The ARN of the OpenSearch Serverless collection."
  value       = aws_opensearchserverless_collection.vector_logs.arn
}

output "collection_endpoint" {
  description = "The collection endpoint for the OpenSearch Serverless collection."
  value       = aws_opensearchserverless_collection.vector_logs.collection_endpoint
}

output "dashboard_endpoint" {
  description = "The OpenSearch Dashboards endpoint for the collection."
  value       = aws_opensearchserverless_collection.vector_logs.dashboard_endpoint
}

output "collection_name" {
  description = "The name of the OpenSearch Serverless collection."
  value       = aws_opensearchserverless_collection.vector_logs.name
}