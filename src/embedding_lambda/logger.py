# src/embedding_lambda/logger.py

import json
import logging
import time
from typing import Any, Dict, Optional
from config import Config

class StructuredLogger:
    """Structured logging for Lambda function with cost tracking."""
    
    def __init__(self, name: str = __name__):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
        
        # Configure handler if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _log_structured(self, level: str, message: str, **kwargs):
        """Log structured JSON message."""
        log_entry = {
            'timestamp': time.time(),
            'level': level,
            'message': message,
            'lambda_request_id': kwargs.pop('lambda_request_id', None),
            **kwargs
        }
        
        # Remove None values
        log_entry = {k: v for k, v in log_entry.items() if v is not None}
        
        getattr(self.logger, level.lower())(json.dumps(log_entry))
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log_structured('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log_structured('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log_structured('ERROR', message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        if Config.ENABLE_DETAILED_LOGGING:
            self._log_structured('DEBUG', message, **kwargs)

class CostTracker:
    """Track and log cost-related metrics."""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.metrics = {
            'total_tokens_processed': 0,
            'total_embeddings_generated': 0,
            'total_api_calls': 0,
            'failed_requests': 0,
            'execution_start_time': time.time()
        }
    
    def track_embedding_request(self, text_length: int, success: bool = True):
        """Track embedding generation request."""
        if not Config.ENABLE_COST_TRACKING:
            return
            
        self.metrics['total_tokens_processed'] += text_length
        self.metrics['total_api_calls'] += 1
        
        if success:
            self.metrics['total_embeddings_generated'] += 1
        else:
            self.metrics['failed_requests'] += 1
    
    def check_cost_limits(self) -> bool:
        """Check if cost limits are exceeded."""
        if not Config.ENABLE_COST_TRACKING:
            return True
            
        if self.metrics['total_tokens_processed'] > Config.MAX_TOKENS_PER_EXECUTION:
            self.logger.warning(
                "Token limit exceeded",
                tokens_processed=self.metrics['total_tokens_processed'],
                limit=Config.MAX_TOKENS_PER_EXECUTION
            )
            return False
        return True
    
    def log_final_metrics(self, lambda_request_id: str):
        """Log final execution metrics."""
        if not Config.ENABLE_COST_TRACKING:
            return
            
        execution_time = time.time() - self.metrics['execution_start_time']
        
        # Estimate costs (approximate pricing)
        estimated_cost = self._estimate_cost()
        
        self.logger.info(
            "Execution completed",
            lambda_request_id=lambda_request_id,
            execution_time_seconds=round(execution_time, 3),
            metrics=self.metrics,
            estimated_cost_usd=estimated_cost
        )
    
    def _estimate_cost(self) -> float:
        """Estimate cost based on usage (approximate Bedrock Titan pricing)."""
        # Approximate pricing: $0.0001 per 1K tokens for Titan embeddings
        token_cost = (self.metrics['total_tokens_processed'] / 1000) * 0.0001
        return round(token_cost, 6)