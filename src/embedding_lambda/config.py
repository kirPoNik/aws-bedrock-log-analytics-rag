# src/embedding_lambda/config.py

import os
from typing import Optional

class Config:
    """Configuration management for the embedding Lambda function."""
    
    # AWS Configuration
    AWS_REGION: str = os.environ.get('AWS_REGION', 'us-east-1')
    
    # Bedrock Configuration
    BEDROCK_MODEL_ID: str = os.environ.get('BEDROCK_MODEL_ID', 'amazon.titan-embed-text-v1')
    BEDROCK_TIMEOUT: int = int(os.environ.get('BEDROCK_TIMEOUT', '30'))
    BEDROCK_MAX_RETRIES: int = int(os.environ.get('BEDROCK_MAX_RETRIES', '3'))
    
    # Processing Configuration
    MAX_TEXT_LENGTH: int = int(os.environ.get('MAX_TEXT_LENGTH', '8000'))
    BATCH_SIZE: int = int(os.environ.get('BATCH_SIZE', '10'))
    ENABLE_CACHING: bool = os.environ.get('ENABLE_CACHING', 'false').lower() == 'true'
    
    # Cost Optimization
    ENABLE_COST_TRACKING: bool = os.environ.get('ENABLE_COST_TRACKING', 'true').lower() == 'true'
    MAX_TOKENS_PER_EXECUTION: int = int(os.environ.get('MAX_TOKENS_PER_EXECUTION', '100000'))
    
    # Logging Configuration
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    ENABLE_DETAILED_LOGGING: bool = os.environ.get('ENABLE_DETAILED_LOGGING', 'false').lower() == 'true'
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration values."""
        try:
            assert cls.MAX_TEXT_LENGTH > 0, "MAX_TEXT_LENGTH must be positive"
            assert cls.BATCH_SIZE > 0, "BATCH_SIZE must be positive"
            assert cls.BEDROCK_TIMEOUT > 0, "BEDROCK_TIMEOUT must be positive"
            assert cls.BEDROCK_MAX_RETRIES >= 0, "BEDROCK_MAX_RETRIES must be non-negative"
            return True
        except AssertionError as e:
            raise ValueError(f"Configuration validation failed: {e}")
    
    @classmethod
    def get_debug_info(cls) -> dict:
        """Get configuration info for debugging (without sensitive data)."""
        return {
            'aws_region': cls.AWS_REGION,
            'bedrock_model_id': cls.BEDROCK_MODEL_ID,
            'bedrock_timeout': cls.BEDROCK_TIMEOUT,
            'max_text_length': cls.MAX_TEXT_LENGTH,
            'batch_size': cls.BATCH_SIZE,
            'enable_caching': cls.ENABLE_CACHING,
            'enable_cost_tracking': cls.ENABLE_COST_TRACKING,
            'log_level': cls.LOG_LEVEL
        }