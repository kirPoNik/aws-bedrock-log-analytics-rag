variable "aws_region" {
  description = "The AWS region where resources are deployed"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "aiops"
}

variable "environment_name" {
  description = "Name of the environment (e.g., dev, prod)"
  type        = string
  default     = "dev"
}

variable "tags" {
  description = "A map of tags to assign to the resources"
  type        = map(string)
  default = {
    Project     = "AIOps Chat With Logs"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}

# Lambda Configuration Variables
variable "lambda_bedrock_model_id" {
  description = "Bedrock model ID for embedding generation in Lambda"
  type        = string
  default     = "amazon.titan-embed-text-v1"
}

variable "lambda_bedrock_timeout" {
  description = "Timeout for Bedrock API calls in Lambda (seconds)"
  type        = number
  default     = 30
}

variable "lambda_bedrock_max_retries" {
  description = "Maximum retries for Bedrock API calls in Lambda"
  type        = number
  default     = 3
}

variable "lambda_max_text_length" {
  description = "Maximum text length for embedding generation in Lambda"
  type        = number
  default     = 8000
}

variable "lambda_batch_size" {
  description = "Batch size for processing records in Lambda"
  type        = number
  default     = 10
}

variable "lambda_enable_caching" {
  description = "Whether to enable embedding caching in Lambda"
  type        = bool
  default     = false
}

variable "lambda_enable_cost_tracking" {
  description = "Whether to enable cost tracking in Lambda"
  type        = bool
  default     = true
}

variable "lambda_max_tokens_per_execution" {
  description = "Maximum tokens processed per Lambda execution"
  type        = number
  default     = 100000
}

variable "lambda_log_level" {
  description = "Log level for Lambda function"
  type        = string
  default     = "INFO"
}

variable "lambda_enable_detailed_logging" {
  description = "Whether to enable detailed logging for Lambda debugging"
  type        = bool
  default     = false
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 300
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 512
}