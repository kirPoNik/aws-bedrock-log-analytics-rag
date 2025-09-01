# modules/ingestion/main.tf

data "aws_region" "current" {}

resource "aws_cloudwatch_log_group" "osis_pipeline_logs" {
  name              = "/aws/vendedlogs/opensearch-ingestion/${var.pipeline_name}"
  retention_in_days = 14
  tags              = var.tags
}

resource "aws_osis_pipeline" "log_embedding_pipeline" {
  pipeline_name = var.pipeline_name
  min_units     = 2
  max_units     = 10

  log_publishing_options {
    is_logging_enabled                 = true
    cloudwatch_log_destination {
      log_group = aws_cloudwatch_log_group.osis_pipeline_logs.name
    }
  }

  pipeline_configuration_body = <<-EOT
  version: "2"
  log-pipeline:
    source:
      http:
        path: "/${var.pipeline_name}/logs"
    processor:
      - aws_lambda:
          function_name: "${var.embedding_lambda_arn}"
          aws:
            region: "${data.aws_region.current.name}"
            sts_role_arn: "${var.ingestion_role_arn}"
    sink:
      - opensearch:
          hosts: ["${var.opensearch_collection_endpoint}"]
          index: "os-vector-index-${var.opensearch_collection_name}"
          aws:
            sts_role_arn: "${var.ingestion_role_arn}"
            region: "${data.aws_region.current.name}"
            serverless: true
  EOT

  tags = var.tags
}