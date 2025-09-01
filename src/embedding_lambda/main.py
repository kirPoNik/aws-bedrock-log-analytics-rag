# src/embedding_lambda/main.py

import json
import boto3
import hashlib
import time
from typing import List, Dict, Optional, Any
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError, BotoCoreError

from config import Config
from logger import StructuredLogger, CostTracker

# Validate configuration on startup
Config.validate()

# Initialize logger and cost tracker
logger = StructuredLogger(__name__)
cost_tracker = CostTracker(logger)

# Initialize the Bedrock Runtime client with retry configuration
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name=Config.AWS_REGION,
    config=BotoConfig(
        retries={'max_attempts': Config.BEDROCK_MAX_RETRIES},
        read_timeout=Config.BEDROCK_TIMEOUT
    )
)

# Simple in-memory cache for embeddings (if enabled)
embedding_cache = {} if Config.ENABLE_CACHING else None

def generate_embedding(text: str, request_id: str = None) -> Optional[List[float]]:
    """Generates an embedding for the given text using the Titan model."""
    # Truncate text if too long
    if len(text) > Config.MAX_TEXT_LENGTH:
        text = text[:Config.MAX_TEXT_LENGTH]
        logger.info(
            "Text truncated for embedding", 
            original_length=len(text), 
            truncated_length=Config.MAX_TEXT_LENGTH,
            lambda_request_id=request_id
        )
    
    # Check cache if enabled
    cache_key = None
    if Config.ENABLE_CACHING and embedding_cache is not None:
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in embedding_cache:
            logger.debug("Cache hit for embedding", cache_key=cache_key, lambda_request_id=request_id)
            cost_tracker.track_embedding_request(len(text), success=True)
            return embedding_cache[cache_key]
    
    # Check cost limits
    if not cost_tracker.check_cost_limits():
        logger.error("Cost limits exceeded, skipping embedding generation", lambda_request_id=request_id)
        return None
    
    body = json.dumps({"inputText": text})
    
    start_time = time.time()
    try:
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=Config.BEDROCK_MODEL_ID,
            accept='application/json',
            contentType='application/json'
        )
        response_body = json.loads(response.get('body').read())
        embedding = response_body.get('embedding')
        
        # Track successful request
        cost_tracker.track_embedding_request(len(text), success=True)
        
        # Cache if enabled
        if Config.ENABLE_CACHING and embedding_cache is not None and cache_key:
            embedding_cache[cache_key] = embedding
        
        execution_time = time.time() - start_time
        logger.info(
            "Embedding generated successfully",
            text_length=len(text),
            execution_time=round(execution_time, 3),
            model_id=Config.BEDROCK_MODEL_ID,
            lambda_request_id=request_id
        )
        
        return embedding
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        cost_tracker.track_embedding_request(len(text), success=False)
        
        logger.error(
            "Bedrock API error",
            error_code=error_code,
            error_message=error_message,
            text_length=len(text),
            lambda_request_id=request_id
        )
        return None
        
    except BotoCoreError as e:
        cost_tracker.track_embedding_request(len(text), success=False)
        logger.error(
            "Boto3 error during embedding generation",
            error=str(e),
            text_length=len(text),
            lambda_request_id=request_id
        )
        return None
        
    except Exception as e:
        cost_tracker.track_embedding_request(len(text), success=False)
        logger.error(
            "Unexpected error during embedding generation",
            error=str(e),
            error_type=type(e).__name__,
            text_length=len(text),
            lambda_request_id=request_id
        )
        return None

def lambda_handler(data: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Receives a batch of log records from OpenSearch Ingestion, 
    generates embeddings, and returns the enriched records.
    """
    request_id = context.aws_request_id if context else 'unknown'
    
    records = data.get('events', [])    
    logger.info(
        "Lambda execution started",
        lambda_request_id=request_id,
        record_count=len(records),
        config=Config.get_debug_info() if Config.ENABLE_DETAILED_LOGGING else None
    )
    
    processed_records = []
    successful_embeddings = 0
    failed_embeddings = 0
    
    # Process records in batches for better performance
    batch_size = min(Config.BATCH_SIZE, len(records)) if records else 1
    batch_size = max(1, batch_size)  # Ensure batch_size is at least 1
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]        
        for record_index, record in enumerate(batch):
            try:                
                log_message = record.get('message', '')
                log_services = record.get('service', [])
                log_user_id = record.get('user_id', '')
                log_level = record.get('level', '')
                full_message = f"{log_services} {log_user_id} {log_level} {log_message}".strip()

                embedding = generate_embedding(full_message, request_id)
                if embedding:
                    # Add the new embedding vector to the log data
                    record['log_embedding'] = embedding
                    record['embedding_model'] = Config.BEDROCK_MODEL_ID
                    record['embedding_timestamp'] = int(time.time())
                    successful_embeddings += 1
                else:
                    failed_embeddings += 1
                    logger.debug(
                        "Failed to generate embedding for record",
                        record_index=i + record_index,
                        message_length=len(log_message),
                        lambda_request_id=request_id
                    )
                
                # Keep the original record structure and append the modified data
                processed_records.append(record)
                
            except Exception as e:
                failed_embeddings += 1
                logger.error(
                    "Error processing record",
                    record_index=i + record_index,
                    error=str(e),
                    error_type=type(e).__name__,
                    lambda_request_id=request_id
                )
                # Include the original record even if processing failed
                processed_records.append(record)
    
    # Log final metrics
    cost_tracker.log_final_metrics(request_id)
    
    logger.info(
        "Lambda execution completed",
        lambda_request_id=request_id,
        total_records=len(records),
        successful_embeddings=successful_embeddings,
        failed_embeddings=failed_embeddings,
        success_rate=round((successful_embeddings / len(records)) * 100, 2) if records else 0
    )
    
    return {"events": processed_records}
