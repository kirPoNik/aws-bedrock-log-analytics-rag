# src/streamlit_app/logger.py

import json
import logging
import time
import streamlit as st
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from config import AppConfig

class StreamlitLogger:
    """Structured logging for Streamlit application."""
    
    def __init__(self, name: str = __name__):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, AppConfig.LOG_LEVEL.upper()))
        
        # Configure handler if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _log_structured(self, level: str, message: str, **kwargs):
        """Log structured message."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            'session_id': self._get_session_id(),
            **kwargs
        }
        
        # Remove None values
        log_entry = {k: v for k, v in log_entry.items() if v is not None}
        
        if AppConfig.ENABLE_DEBUG_MODE:
            # Also log to Streamlit sidebar in debug mode
            with st.sidebar:
                st.json(log_entry)
        
        getattr(self.logger, level.lower())(json.dumps(log_entry))
    
    def _get_session_id(self) -> str:
        """Get Streamlit session ID."""
        try:
            return st.session_state.get('session_id', 'unknown')
        except:
            return 'unknown'
    
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
        if AppConfig.ENABLE_DEBUG_MODE:
            self._log_structured('DEBUG', message, **kwargs)

class CostTracker:
    """Track and display cost-related metrics for the Streamlit app."""
    
    def __init__(self, logger: StreamlitLogger):
        self.logger = logger
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state for cost tracking."""
        if 'cost_metrics' not in st.session_state:
            st.session_state.cost_metrics = {
                'session_start_time': time.time(),
                'total_queries': 0,
                'total_tokens_processed': 0,
                'total_embeddings_generated': 0,
                'total_llm_requests': 0,
                'estimated_cost': 0.0,
                'hourly_requests': []
            }
    
    def track_query(self, query_length: int):
        """Track a user query."""
        if not AppConfig.ENABLE_COST_TRACKING:
            return
        
        metrics = st.session_state.cost_metrics
        metrics['total_queries'] += 1
        
        # Add to hourly tracking
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        metrics['hourly_requests'].append(current_hour)
        
        # Clean old entries (keep only last 24 hours)
        cutoff_time = current_hour - timedelta(hours=24)
        metrics['hourly_requests'] = [
            req_time for req_time in metrics['hourly_requests'] 
            if req_time >= cutoff_time
        ]
        
        self.logger.info(
            "Query tracked",
            query_length=query_length,
            total_queries=metrics['total_queries']
        )
    
    def track_embedding_request(self, text_length: int):
        """Track embedding generation request."""
        if not AppConfig.ENABLE_COST_TRACKING:
            return
        
        metrics = st.session_state.cost_metrics
        metrics['total_tokens_processed'] += text_length
        metrics['total_embeddings_generated'] += 1
        
        # Update estimated cost (approximate Bedrock Titan pricing)
        token_cost = (text_length / 1000) * 0.0001  # $0.0001 per 1K tokens
        metrics['estimated_cost'] += token_cost
    
    def track_llm_request(self, input_tokens: int, output_tokens: int):
        """Track LLM (Claude) request."""
        if not AppConfig.ENABLE_COST_TRACKING:
            return
        
        metrics = st.session_state.cost_metrics
        metrics['total_llm_requests'] += 1
        
        # Approximate Claude pricing: $3 per 1M input tokens, $15 per 1M output tokens
        input_cost = (input_tokens / 1000000) * 3.0
        output_cost = (output_tokens / 1000000) * 15.0
        metrics['estimated_cost'] += input_cost + output_cost
        
        self.logger.info(
            "LLM request tracked",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost=input_cost + output_cost
        )
    
    def check_rate_limits(self) -> bool:
        """Check if rate limits are exceeded."""
        if not AppConfig.ENABLE_COST_TRACKING:
            return True
        
        metrics = st.session_state.cost_metrics
        
        # Check hourly rate limit
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        recent_requests = [
            req_time for req_time in metrics['hourly_requests']
            if req_time >= current_hour - timedelta(hours=1)
        ]
        
        if len(recent_requests) >= AppConfig.MAX_REQUESTS_PER_HOUR:
            self.logger.warning(
                "Hourly rate limit exceeded",
                requests_last_hour=len(recent_requests),
                limit=AppConfig.MAX_REQUESTS_PER_HOUR
            )
            return False
        
        # Check session token limit
        if metrics['total_tokens_processed'] > AppConfig.MAX_TOKENS_PER_SESSION:
            self.logger.warning(
                "Session token limit exceeded",
                tokens_processed=metrics['total_tokens_processed'],
                limit=AppConfig.MAX_TOKENS_PER_SESSION
            )
            return False
        
        return True
    
    def display_metrics(self):
        """Display cost metrics in Streamlit sidebar."""
        if not AppConfig.ENABLE_COST_TRACKING:
            return
        
        metrics = st.session_state.cost_metrics
        session_duration = time.time() - metrics['session_start_time']
        
        with st.sidebar:
            st.subheader("📊 Usage Metrics")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Queries", metrics['total_queries'])
                st.metric("Embeddings", metrics['total_embeddings_generated'])
            
            with col2:
                st.metric("LLM Calls", metrics['total_llm_requests'])
                st.metric("Est. Cost", f"${metrics['estimated_cost']:.4f}")
            
            # Rate limiting info
            current_hour_requests = len([
                req for req in metrics['hourly_requests']
                if req >= datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
            ])
            
            st.progress(
                current_hour_requests / AppConfig.MAX_REQUESTS_PER_HOUR,
                text=f"Rate Limit: {current_hour_requests}/{AppConfig.MAX_REQUESTS_PER_HOUR} requests/hour"
            )
            
            st.progress(
                metrics['total_tokens_processed'] / AppConfig.MAX_TOKENS_PER_SESSION,
                text=f"Tokens: {metrics['total_tokens_processed']:,}/{AppConfig.MAX_TOKENS_PER_SESSION:,}"
            )
            
            if AppConfig.ENABLE_DEBUG_MODE:
                st.json({
                    'session_duration_minutes': round(session_duration / 60, 2),
                    'avg_query_length': round(metrics['total_tokens_processed'] / max(metrics['total_queries'], 1), 2)
                })


class QueryCache:
    """Simple query result caching to reduce API calls."""
    
    def __init__(self, logger: StreamlitLogger):
        self.logger = logger
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state for caching."""
        if 'query_cache' not in st.session_state:
            st.session_state.query_cache = {}
    
    def get_cache_key(self, query: str, search_size: int) -> str:
        """Generate cache key for query."""
        return f"{hash(query)}_{search_size}"
    
    def get(self, query: str, search_size: int) -> Optional[Dict[str, Any]]:
        """Get cached result if available."""
        if not AppConfig.ENABLE_QUERY_CACHING:
            return None
        
        cache_key = self.get_cache_key(query, search_size)
        cached_result = st.session_state.query_cache.get(cache_key)
        
        if cached_result:
            # Check if cache is still valid (5 minutes)
            if time.time() - cached_result['timestamp'] < 300:
                self.logger.info("Cache hit", cache_key=cache_key, query=query[:50])
                return cached_result['data']
            else:
                # Remove expired cache entry
                del st.session_state.query_cache[cache_key]
        
        return None
    
    def set(self, query: str, search_size: int, result: Dict[str, Any]):
        """Cache query result."""
        if not AppConfig.ENABLE_QUERY_CACHING:
            return
        
        cache_key = self.get_cache_key(query, search_size)
        st.session_state.query_cache[cache_key] = {
            'timestamp': time.time(),
            'data': result
        }
        
        # Limit cache size (keep only 50 most recent)
        if len(st.session_state.query_cache) > 50:
            oldest_key = min(
                st.session_state.query_cache.keys(),
                key=lambda k: st.session_state.query_cache[k]['timestamp']
            )
            del st.session_state.query_cache[oldest_key]
        
        self.logger.info("Result cached", cache_key=cache_key, query=query[:50])