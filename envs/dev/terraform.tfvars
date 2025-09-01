aws_region       = "us-east-1"
project_name     = "aiops"
environment_name = "dev"

# Set to true if you want to deploy resources in a VPC
create_vpc = false

# VPC Configuration (only used if create_vpc = true)
vpc_cidr             = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.10.0/24", "10.0.20.0/24"]
create_nat_gateway   = false
create_vpc_endpoints = false

# Lambda Configuration (Development Settings)
lambda_bedrock_model_id              = "amazon.titan-embed-text-v2:0"
lambda_bedrock_timeout               = 30
lambda_bedrock_max_retries           = 3
lambda_max_text_length               = 8000
lambda_batch_size                    = 10
lambda_enable_caching                = true   # Enable caching for dev to reduce costs
lambda_enable_cost_tracking          = true
lambda_max_tokens_per_execution      = 50000  # Lower limit for dev environment
lambda_log_level                     = "DEBUG" # More verbose logging for development
lambda_enable_detailed_logging       = true   # Detailed logging for debugging
lambda_timeout                       = 300    # 5 minutes
lambda_memory_size                   = 512    # 512 MB for dev

tags = {
  Project     = "AIOps Chat With Logs"
  Environment = "dev"
  ManagedBy   = "Terraform"
}
