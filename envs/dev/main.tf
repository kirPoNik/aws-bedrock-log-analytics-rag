terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    opensearch = {
      source  = "opensearch-project/opensearch"
      version = "= 2.2.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

provider "opensearch" {
  url         = module.opensearch.collection_endpoint
  healthcheck = false
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
  prefix     = "${var.project_name}-${var.environment_name}"
}

module "opensearch" {
  source = "../../modules/opensearch"

  collection_name           = "${local.prefix}-logs"
  access_policy_principals = [
    data.aws_caller_identity.current.arn,
    module.iam.opensearch_ingestion_role_arn,
    module.iam.lambda_execution_role_arn
  ]
  tags = var.tags
}

module "iam" {
  source = "../../modules/iam"

  collection_arn         = module.opensearch.collection_arn
  pipeline_name          = "${local.prefix}-pipeline"
  lambda_function_name   = "${local.prefix}-embedding-lambda"
  lambda_bedrock_model_id = var.lambda_bedrock_model_id
  aws_region             = data.aws_region.current.name
  aws_account_id         = local.account_id
}

module "lambda_chatapp" {
  source = "../../modules/embedding_lambda"

  function_name   = "${local.prefix}-embedding-lambda"
  source_code_path = "../../src/embedding_lambda"
  lambda_role_arn = module.iam.lambda_execution_role_arn
  
  # Lambda Configuration
  bedrock_model_id           = var.lambda_bedrock_model_id
  bedrock_timeout            = var.lambda_bedrock_timeout
  bedrock_max_retries        = var.lambda_bedrock_max_retries
  max_text_length            = var.lambda_max_text_length
  batch_size                 = var.lambda_batch_size
  enable_caching             = var.lambda_enable_caching
  enable_cost_tracking       = var.lambda_enable_cost_tracking
  max_tokens_per_execution   = var.lambda_max_tokens_per_execution
  log_level                  = var.lambda_log_level
  enable_detailed_logging    = var.lambda_enable_detailed_logging
  lambda_timeout             = var.lambda_timeout
  lambda_memory_size         = var.lambda_memory_size
  
  tags = var.tags
}

module "ingestion" {
  source = "../../modules/ingestion_pipeline"

  pipeline_name                  = "${local.prefix}-pipeline"
  opensearch_collection_endpoint = module.opensearch.collection_endpoint
  opensearch_collection_name     = module.opensearch.collection_name
  embedding_lambda_arn           = module.lambda_chatapp.lambda_function_arn
  ingestion_role_arn             = module.iam.opensearch_ingestion_role_arn
  tags                           = var.tags
}
