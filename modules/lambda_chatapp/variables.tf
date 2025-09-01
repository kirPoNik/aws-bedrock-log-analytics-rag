# modules/lambda_chatapp/variables.tf

variable "function_name" {
  description = "The name of the Lambda function."
  type        = string
}

variable "source_code_path" {
  description = "The local path to the Lambda function's source code."
  type        = string
}

variable "lambda_role_arn" {
  description = "The ARN of the IAM role for the Lambda function."
  type        = string
}

variable "tags" {
  description = "A map of tags to assign to the resources."
  type        = map(string)
  default     = {}
}

# Lambda Configuration Variables
variable "bedrock_model_id" {
  description = "Bedrock model ID for embedding generation."
  type        = string
  default     = "amazon.titan-embed-text-v1"
}

variable "bedrock_timeout" {
  description = "Timeout for Bedrock API calls in seconds."
  type        = number
  default     = 30
}

variable "bedrock_max_retries" {
  description = "Maximum retries for Bedrock API calls."
  type        = number
  default     = 3
}

variable "max_text_length" {
  description = "Maximum text length for embedding generation."
  type        = number
  default     = 8000
}

variable "batch_size" {
  description = "Batch size for processing records."
  type        = number
  default     = 10
}

variable "enable_caching" {
  description = "Whether to enable embedding caching."
  type        = bool
  default     = false
}

variable "enable_cost_tracking" {
  description = "Whether to enable cost tracking."
  type        = bool
  default     = true
}

variable "max_tokens_per_execution" {
  description = "Maximum tokens processed per Lambda execution."
  type        = number
  default     = 100000
}

variable "log_level" {
  description = "Log level for the Lambda function."
  type        = string
  default     = "INFO"
  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR"], var.log_level)
    error_message = "Log level must be one of: DEBUG, INFO, WARNING, ERROR."
  }
}

variable "enable_detailed_logging" {
  description = "Whether to enable detailed logging for debugging."
  type        = bool
  default     = false
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds."
  type        = number
  default     = 300
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB."
  type        = number
  default     = 512
}
