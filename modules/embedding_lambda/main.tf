module "embedding_lambda" {
  source = "terraform-aws-modules/lambda/aws"
  version = "7.2.1"

  function_name = var.function_name
  description   = "Lambda function to generate embeddings for logs using Bedrock"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"
  source_path   = var.source_code_path
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  create_role     = false
  lambda_role     = var.lambda_role_arn

  environment_variables = {
    # Bedrock Configuration
    BEDROCK_MODEL_ID = var.bedrock_model_id
    BEDROCK_TIMEOUT = tostring(var.bedrock_timeout)
    BEDROCK_MAX_RETRIES = tostring(var.bedrock_max_retries)
    
    # Processing Configuration
    MAX_TEXT_LENGTH = tostring(var.max_text_length)
    BATCH_SIZE = tostring(var.batch_size)
    ENABLE_CACHING = tostring(var.enable_caching)
    
    # Cost Optimization
    ENABLE_COST_TRACKING = tostring(var.enable_cost_tracking)
    MAX_TOKENS_PER_EXECUTION = tostring(var.max_tokens_per_execution)
    
    # Logging Configuration
    LOG_LEVEL = var.log_level
    ENABLE_DETAILED_LOGGING = tostring(var.enable_detailed_logging)
  }
  
  tags = var.tags
}
