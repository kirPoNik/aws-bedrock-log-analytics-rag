# src/streamlit_app/config.py

import os
import streamlit as st
from typing import Dict, Any

class AppConfig:
    """Configuration management for the Streamlit application."""
    
    # AWS Configuration
    AWS_REGION: str = os.environ.get('AWS_REGION', st.secrets.get('AWS_REGION', 'us-east-1'))
    
    # OpenSearch Configuration
    OPENSEARCH_HOST: str = os.environ.get(
        'OPENSEARCH_HOST', 
        st.secrets.get('OPENSEARCH_HOST', 'YOUR_OPENSEARCH_SERVERLESS_ENDPOINT')
    )
    INDEX_NAME: str = os.environ.get('INDEX_NAME', st.secrets.get('INDEX_NAME', 'application-logs-*'))
    
    # Bedrock Configuration
    BEDROCK_MODEL_ID_EMBEDDING: str = os.environ.get(
        'BEDROCK_MODEL_ID_EMBEDDING',
        st.secrets.get('BEDROCK_MODEL_ID_EMBEDDING', 'amazon.titan-embed-text-v1')
    )
    BEDROCK_MODEL_ID_CLAUDE: str = os.environ.get(
        'BEDROCK_MODEL_ID_CLAUDE',
        st.secrets.get('BEDROCK_MODEL_ID_CLAUDE', 'anthropic.claude-3-sonnet-20240229-v1:0')
    )
    BEDROCK_TIMEOUT: int = int(os.environ.get('BEDROCK_TIMEOUT', st.secrets.get('BEDROCK_TIMEOUT', '30')))
    BEDROCK_MAX_RETRIES: int = int(os.environ.get('BEDROCK_MAX_RETRIES', st.secrets.get('BEDROCK_MAX_RETRIES', '3')))
    
    # Search Configuration
    DEFAULT_SEARCH_SIZE: int = int(os.environ.get('DEFAULT_SEARCH_SIZE', st.secrets.get('DEFAULT_SEARCH_SIZE', '10')))
    MAX_SEARCH_SIZE: int = int(os.environ.get('MAX_SEARCH_SIZE', st.secrets.get('MAX_SEARCH_SIZE', '50')))
    
    # UI Configuration
    PAGE_TITLE: str = os.environ.get('PAGE_TITLE', st.secrets.get('PAGE_TITLE', 'Chat with Your Logs'))
    MAX_QUERY_LENGTH: int = int(os.environ.get('MAX_QUERY_LENGTH', st.secrets.get('MAX_QUERY_LENGTH', '500')))
    
    # Cost Optimization
    ENABLE_COST_TRACKING: bool = os.environ.get('ENABLE_COST_TRACKING', st.secrets.get('ENABLE_COST_TRACKING', 'true')).lower() == 'true'
    MAX_TOKENS_PER_SESSION: int = int(os.environ.get('MAX_TOKENS_PER_SESSION', st.secrets.get('MAX_TOKENS_PER_SESSION', '500000')))
    ENABLE_QUERY_CACHING: bool = os.environ.get('ENABLE_QUERY_CACHING', st.secrets.get('ENABLE_QUERY_CACHING', 'true')).lower() == 'true'
    
    # Rate Limiting
    MAX_REQUESTS_PER_HOUR: int = int(os.environ.get('MAX_REQUESTS_PER_HOUR', st.secrets.get('MAX_REQUESTS_PER_HOUR', '100')))
    
    # Logging Configuration
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', st.secrets.get('LOG_LEVEL', 'INFO'))
    ENABLE_DEBUG_MODE: bool = os.environ.get('ENABLE_DEBUG_MODE', st.secrets.get('ENABLE_DEBUG_MODE', 'false')).lower() == 'true'
    
    @classmethod
    def validate(cls) -> Dict[str, str]:
        """Validate configuration and return any errors."""
        errors = {}
        
        if cls.OPENSEARCH_HOST == 'YOUR_OPENSEARCH_SERVERLESS_ENDPOINT':
            errors['opensearch_host'] = 'Please configure OpenSearch host endpoint'
        
        if cls.MAX_SEARCH_SIZE < cls.DEFAULT_SEARCH_SIZE:
            errors['search_size'] = 'MAX_SEARCH_SIZE must be >= DEFAULT_SEARCH_SIZE'
        
        if cls.MAX_QUERY_LENGTH <= 0:
            errors['query_length'] = 'MAX_QUERY_LENGTH must be positive'
        
        if cls.MAX_TOKENS_PER_SESSION <= 0:
            errors['token_limit'] = 'MAX_TOKENS_PER_SESSION must be positive'
        
        return errors
    
    @classmethod
    def get_debug_info(cls) -> Dict[str, Any]:
        """Get configuration info for debugging (without sensitive data)."""
        return {
            'aws_region': cls.AWS_REGION,
            'opensearch_configured': cls.OPENSEARCH_HOST != 'YOUR_OPENSEARCH_SERVERLESS_ENDPOINT',
            'index_name': cls.INDEX_NAME,
            'bedrock_embedding_model': cls.BEDROCK_MODEL_ID_EMBEDDING,
            'bedrock_claude_model': cls.BEDROCK_MODEL_ID_CLAUDE,
            'default_search_size': cls.DEFAULT_SEARCH_SIZE,
            'max_search_size': cls.MAX_SEARCH_SIZE,
            'cost_tracking_enabled': cls.ENABLE_COST_TRACKING,
            'caching_enabled': cls.ENABLE_QUERY_CACHING,
            'debug_mode': cls.ENABLE_DEBUG_MODE
        }