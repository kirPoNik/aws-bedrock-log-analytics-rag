# src/streamlit_app/app.py

import streamlit as st
import boto3
import json
import time
import hashlib
from typing import List, Dict, Any, Optional
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from config import AppConfig
from logger import StreamlitLogger, CostTracker, QueryCache

# Initialize configuration and validate
config_errors = AppConfig.validate()
if config_errors:
    st.error("Configuration errors detected:")
    for key, error in config_errors.items():
        st.error(f"• {error}")
    st.stop()

# Initialize logger, cost tracker, and cache
logger = StreamlitLogger(__name__)
cost_tracker = CostTracker(logger)
query_cache = QueryCache(logger)

# Initialize session ID for tracking
if 'session_id' not in st.session_state:
    st.session_state.session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]

logger.info("Streamlit app started", config=AppConfig.get_debug_info())

# --- Boto3 and OpenSearch Clients ---
try:
    session = boto3.Session()
    credentials = session.get_credentials()
    
    if not credentials:
        st.error("❌ AWS credentials not found. Please configure AWS credentials.")
        st.stop()
    
    awsauth = AWS4Auth(
        credentials.access_key, 
        credentials.secret_key, 
        AppConfig.AWS_REGION, 
        'aoss', 
        session_token=credentials.token
    )
    
    bedrock_runtime = session.client(
        'bedrock-runtime', 
        region_name=AppConfig.AWS_REGION,
        config=BotoConfig(
            retries={'max_attempts': AppConfig.BEDROCK_MAX_RETRIES},
            read_timeout=AppConfig.BEDROCK_TIMEOUT
        )
    )
    
    os_client = OpenSearch(
        hosts=[{'host': AppConfig.OPENSEARCH_HOST, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        pool_maxsize=20
    )
    
    logger.info("AWS clients initialized successfully")
    
except Exception as e:
    logger.error("Failed to initialize AWS clients", error=str(e))
    st.error(f"❌ Failed to initialize AWS clients: {e}")
    st.stop()

# --- Functions ---
def get_embedding(text: str) -> Optional[List[float]]:
    """Generates an embedding for the given text using the Titan model."""
    if not text or not text.strip():
        logger.warning("Empty text provided for embedding")
        return None
    
    # Track the request
    cost_tracker.track_embedding_request(len(text))
    
    body = json.dumps({"inputText": text})
    
    start_time = time.time()
    try:
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=AppConfig.BEDROCK_MODEL_ID_EMBEDDING,
            accept='application/json',
            contentType='application/json'
        )
        response_body = json.loads(response.get('body').read())
        embedding = response_body.get('embedding')
        
        execution_time = time.time() - start_time
        logger.info(
            "Embedding generated",
            text_length=len(text),
            execution_time=round(execution_time, 3),
            model_id=AppConfig.BEDROCK_MODEL_ID_EMBEDDING
        )
        
        return embedding
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error("Bedrock API error", error_code=error_code, error_message=error_message)
        st.error(f"❌ Bedrock API error: {error_message}")
        return None
        
    except Exception as e:
        logger.error("Unexpected error during embedding generation", error=str(e))
        st.error(f"❌ Error generating embedding: {e}")
        return None

def search_logs(query_vector, k=10):
    """Performs a k-NN search on the OpenSearch index."""
    if query_vector is None:
        return []
    
    query = {
        "size": k,
        "query": {
            "knn": {
                "log_embedding": {
                    "vector": query_vector,
                    "k": k
                }
            }
        }
    }
    try:
        response = os_client.search(index=AppConfig.INDEX_NAME, body=query)
        return [hit['_source']['message'] for hit in response['hits']['hits']]
    except Exception as e:
        st.error(f"Error searching logs: {e}")
        return []

def get_llm_response(question, logs):
    """Sends the retrieved logs and question to Claude for a synthesized answer."""
    log_context = "\n".join(logs)
    
    prompt = f"""
    You are an expert AIOps assistant. Your task is to answer questions about application behavior based *only* on the provided log entries. Do not use any prior knowledge. If the answer cannot be found in the logs, you must state 'I cannot answer the question based on the provided logs.'

    Here are the relevant log entries retrieved:
    <logs>
    {log_context}
    </logs>

    Based on the logs above, please answer the following question:
    <question>
    {question}
    </question>
    """
    
    return prompt
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    })
    
    try:
        response = bedrock_runtime.invoke_model(body=body, modelId=BEDROCK_MODEL_ID_CLAUDE)
        response_body = json.loads(response.get('body').read())
        return response_body['content'][0]['text']
    except Exception as e:
        st.error(f"Error getting LLM response: {e}")
        return "An error occurred while generating the answer."

# --- Streamlit UI ---
st.set_page_config(page_title="Chat with Your Logs", layout="wide")
st.title("💬 Chat with Your Logs")

st.info("This is a demo application. Please replace `YOUR_OPENSEARCH_SERVERLESS_ENDPOINT` in the script with the actual endpoint from your Terraform deployment.")

user_question = st.text_input("Ask a question about the application logs:", key="user_question")

if st.button("Get Answer", key="get_answer"):
    if user_question:
        with st.spinner("Analyzing logs..."):
            # 1. Embed the user's question
            st.write("Step 1: Generating embedding for your question...")
            query_embedding = get_embedding(user_question)
            
            # 2. Perform k-NN search to find relevant logs
            st.write("Step 2: Searching for relevant logs in OpenSearch...")
            relevant_logs = search_logs(query_embedding)
            
            if not relevant_logs:
                st.warning("No relevant logs found for your question.")
            else:
                st.write(f"Step 3: Found {len(relevant_logs)} relevant logs. Synthesizing an answer with Claude...")
                # 3. Get a synthesized answer from the LLM
                answer = get_llm_response(user_question, relevant_logs)
                st.success("Answer:")
                st.markdown(answer)

                with st.expander("See retrieved logs used as context"):
                    st.json(relevant_logs)
    else:
        st.warning("Please enter a question.")
