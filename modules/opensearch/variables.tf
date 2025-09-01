variable "collection_name" {
  description = "The name of the OpenSearch Serverless collection."
  type        = string
}

variable "access_policy_principals" {
  description = "A list of IAM principal ARNs to grant data access."
  type        = list(string)
}

variable "allow_public_access" {
  description = "Whether to allow public access to the OpenSearch collection. Set to false for production."
  type        = bool
  default     = true
}

variable "vpc_endpoints" {
  description = "List of VPC endpoint IDs for private access. Required when allow_public_access is false."
  type        = list(string)
  default     = []
}

variable "use_customer_managed_key" {
  description = "Whether to use a customer-managed KMS key for encryption instead of AWS-owned key."
  type        = bool
  default     = false
}

variable "kms_key_id" {
  description = "KMS key ID for customer-managed encryption. Required when use_customer_managed_key is true."
  type        = string
  default     = null
}


variable "tags" {
  description = "A map of tags to assign to the resources."
  type        = map(string)
  default     = {}
}


# – OpenSearch Serverless Index – 
variable "index_knn_algo_param_ef_search" {
    description = "The size of the dynamic list used during k-NN searches. Higher values lead to more accurate but slower searches."
    type        = string
    default     = "512"
}

variable "number_of_shards" {
    description = "The number of shards for the index. This setting cannot be changed after index creation."
    type        = string
    default     = "1"
}

variable "number_of_replicas" {
   description = "The number of replica shards." 
   type        = string
   default     = "1"
}

variable "force_destroy_vector_index" {
   description = "Whether or not to force destroy the vector index."
   type        = bool
   default     = true
}

variable "vector_index_mappings" {
  description = "A JSON string defining how documents in the index, and the fields they contain, are stored and indexed. To avoid the complexities of field mapping updates, updates of this field are not allowed via this provider."
  type        = string
  default     = <<EOF
{
  "dynamic": true,
  "properties": {
    "request_id": {
      "type": "keyword"
    },
    "service": {
      "type": "keyword"
    },
    "user_id": {
      "type": "keyword"
    },
    "embedding_model": {
      "type": "keyword"
    },
    "level": {
      "type": "keyword"
    },
    "log_embedding": {
      "type": "knn_vector",
      "dimension": 1024,
      "method": {
        "name": "hnsw",
        "space_type": "l2",
        "engine": "nmslib",
        "parameters": {
          "m": 16,
          "ef_construction": 512
        }
      }
    },
    "message": {
      "type": "text"
    },
    "timestamp": {
      "type": "date"
    }
  }
}
EOF
}
