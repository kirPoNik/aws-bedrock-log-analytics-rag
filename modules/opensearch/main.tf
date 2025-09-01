# modules/opensearch/main.tf
terraform {
  required_providers {
    opensearch = {
      source  = "opensearch-project/opensearch"
      version = "= 2.2.0"
    }
  }
}

resource "aws_opensearchserverless_collection" "vector_logs" {
  name = var.collection_name
  type = "VECTORSEARCH"

  tags = var.tags

  depends_on = [
    aws_opensearchserverless_security_policy.network,
    aws_opensearchserverless_security_policy.encryption,
    aws_opensearchserverless_access_policy.data_access
  ]
}
resource "aws_opensearchserverless_security_policy" "encryption" {
  name   = "${var.collection_name}-encryption"
  type   = "encryption"
  policy = jsonencode({
    Rules = [
      {
        Resource     = ["collection/${var.collection_name}"]
        ResourceType = "collection"
      }
    ],
    AWSOwnedKey = true
  })
}

resource "aws_opensearchserverless_security_policy" "network" {
  name   = "${var.collection_name}-network"
  type   = "network"
  policy = jsonencode([
    {
      Rules = [
        {
          Resource     = ["collection/${var.collection_name}"]
          ResourceType = "collection"
        }
      ],
      AllowFromPublic = true
    },
    {
      Rules = [
        {
          Resource     = ["collection/${var.collection_name}"]
          ResourceType = "dashboard"
        }
      ],
      AllowFromPublic = true
    }
  ])
}

resource "aws_opensearchserverless_access_policy" "data_access" {
  name = "${var.collection_name}-data-access"
  type = "data"
  policy = jsonencode([
    {
      Rules = [
        {
          ResourceType = "collection",
          Resource     = ["collection/${var.collection_name}"],
          Permission   = ["aoss:*"]
        },
        {
          ResourceType = "index",
          Resource     = ["index/${var.collection_name}/*"],
          Permission   = ["aoss:*"]
        }
      ],
      Principal = var.access_policy_principals
    }
  ])
}

resource "time_sleep" "wait_before_index_creation" {
  depends_on      = [aws_opensearchserverless_access_policy.data_access]
  create_duration = "60s" # Wait for 60 seconds before creating the index
}

resource "opensearch_index" "vector_index" {
  name                           = "os-vector-index-${var.collection_name}"
  number_of_shards               = var.number_of_shards
  number_of_replicas             = var.number_of_replicas
  index_knn                      = true
  index_knn_algo_param_ef_search = var.index_knn_algo_param_ef_search
  mappings                       = var.vector_index_mappings
  force_destroy                  = var.force_destroy_vector_index
  depends_on                     = [time_sleep.wait_before_index_creation, aws_opensearchserverless_access_policy.data_access]
  lifecycle {
    ignore_changes = [
      number_of_shards,
      number_of_replicas
    ]
  }
}