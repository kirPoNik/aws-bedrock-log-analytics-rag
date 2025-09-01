output "pipeline_ingestion_url" {
  description = "The full URL for the pipeline's HTTP source."
  value       = [ for url in aws_osis_pipeline.log_embedding_pipeline.ingest_endpoint_urls : "https://${url}/${var.pipeline_name}/logs" ]
}