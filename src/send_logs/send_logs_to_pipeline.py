import csv
import json
import requests
from requests_aws4auth import AWS4Auth
import boto3
import time
from typing import List, Dict
import sys

# Configuration
CSV_FILE = "sample_logs.csv"
PIPELINE_URL = "https://aiops-dev-pipeline-<pipeline_id>.<region>.osis.amazonaws.com/aiops-dev-pipeline/logs"
AWS_REGION = "us-east-1"
BATCH_SIZE = 5
DELAY_BETWEEN_BATCHES = 2

current_directory = sys.path[0]
csv_file_path = f"{current_directory}/{CSV_FILE}"


def get_aws_auth() -> AWS4Auth:
    """Get AWS authentication for OSIS requests."""
    try:
        credentials = boto3.Session().get_credentials()
        return AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            AWS_REGION,
            'osis',
            session_token=credentials.token
        )
    except Exception as e:
        print(f"Error getting AWS credentials: {e}")
        sys.exit(1)

def read_logs_from_csv(filename: str) -> List[Dict]:
    """Read log entries from CSV file."""
    logs = []
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert empty strings to None for optional fields
                log_entry = {}
                for key, value in row.items():
                    if value.strip():  # If not empty
                        # Convert numeric fields
                        if key in ['duration_ms', 'status_code']:
                            try:
                                log_entry[key] = int(value)
                            except ValueError:
                                log_entry[key] = value
                        else:
                            log_entry[key] = value
                    else:
                        log_entry[key] = None
                logs.append(log_entry)
        print(f"Successfully read {len(logs)} log entries from {filename}")
        return logs
    except FileNotFoundError:
        print(f"Error: CSV file {filename} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

def send_batch_to_pipeline(logs_batch: List[Dict], auth: AWS4Auth, url: str) -> bool:
    """Send a batch of logs to the OSIS pipeline."""
    try:
        # Send as JSON array
        payload = json.dumps(logs_batch)
        
        print(f"Sending batch of {len(logs_batch)} logs...")
        print(f"Payload preview: {payload[:200]}...")
        
        response = requests.post(
            url,
            data=payload,
            auth=auth,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'LogSender/1.0'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"Batch sent successfully (Status: {response.status_code})")
            return True
        else:
            print(f"Failed to send batch (Status: {response.status_code})")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("Request timed out")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def create_batches(logs: List[Dict], batch_size: int) -> List[List[Dict]]:
    """Split logs into batches of specified size."""
    batches = []
    for i in range(0, len(logs), batch_size):
        batch = logs[i:i + batch_size]
        batches.append(batch)
    return batches

def main():
    auth = get_aws_auth()
    logs = read_logs_from_csv(csv_file_path)
    # Create batches
    batches = create_batches(logs, BATCH_SIZE)
    successful_batches = 0
    failed_batches = 0
    for i, batch in enumerate(batches, 1):
        if send_batch_to_pipeline(batch, auth, PIPELINE_URL):
            successful_batches += 1
        else:
            failed_batches += 1
        if i < len(batches):
            time.sleep(DELAY_BETWEEN_BATCHES)
    
    if failed_batches == 0:
        print("All logs sent successfully!")
    else:
        print("Some batches failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
