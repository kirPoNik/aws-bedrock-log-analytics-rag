#!/usr/bin/env python3

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import json

def search_opensearch_logs(endpoint, query="*", size=10):
    """
    Simple function to search logs in OpenSearch
    """
    # Get AWS credentials
    session = boto3.Session()
    credentials = session.get_credentials()
    region = session.region_name or 'us-east-1'
    
    # Setup authentication
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        'aoss',
        session_token=credentials.token
    )
    
    # Create OpenSearch client
    host = endpoint.replace('https://', '').replace('http://', '')
    client = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    
    # Search logs
    search_body = {
        "query": {
            "query_string": {
                "query": query
            }
        },
        "size": size,
        "sort": [{"timestamp": {"order": "desc"}}]
    }
    
    try:
        response = client.search(index="os-vector-index-aiops-dev-logs", body=search_body)
        return response['hits']['hits']
    except Exception as e:
        print(f"Error: {e}")
        return []

# Example usage
if __name__ == "__main__":
    endpoint = "https://<collection_id>.<region>.aoss.amazonaws.aom"
    results = search_opensearch_logs(endpoint, query="ERROR", size=5)
    
    for hit in results:
        print(json.dumps(hit['_source'], indent=2))
        print("-" * 50)
