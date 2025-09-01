# AIOps: Chat with Your Logs on AWS

This repository contains the complete Infrastructure as Code (IaC) using Terraform to deploy the "Chat with Your Logs" system on AWS. The system leverages Amazon OpenSearch Serverless for vector storage and Amazon Bedrock for embedding generation and natural language synthesis.

## Architecture Overview

The architecture is fully serverless and consists of:

- **Amazon OpenSearch Ingestion:** Receives logs via an HTTP endpoint.
- **AWS Lambda:** A processor function that generates vector embeddings for logs using Amazon Titan.
- **Amazon OpenSearch Serverless:** A `VECTORSEARCH` collection to store and index the logs and their embeddings.
- **Amazon Bedrock:** Provides the Titan embedding model and the Claude synthesis model.
- **Streamlit UI:** A simple web application for users to ask questions.

For a detailed architectural breakdown, please refer to the main report.

## Repository Structure

This repository follows a modular Terraform structure to promote reusability and maintainability.

- `./envs`: Contains environment-specific configurations (e.g., `dev`, `prod`). This is where you run `terraform apply`.
- `./modules`: Contains reusable Terraform modules for each logical component of the architecture (IAM, OpenSearch, etc.).
- `./src`: Contains the Python source code for the embedding Lambda function and the Streamlit UI.

## Deployment Instructions

### Prerequisites

- AWS CLI configured with appropriate credentials.
- Terraform v1.2.0+ installed.
- Python 3.9+ installed.

### Steps

1. **Configure Environment Variables:**
    Navigate to the desired environment directory, for example, `envs/dev/`.
    Open the `terraform.tfvars` file and customize the variables for your deployment (e.g., `aws_region`, `environment_name`).
2. **Initialize Terraform:**
    From within the `envs/dev/` directory, run:
    ```Bash
    terraform init
    ```
3. **Review the Plan**
    ```Bash
    terraform plan
    ```
    This command will show you all the AWS resources that will be created. Review it carefully.
4. **Apply the Configuration:**
    ```Bash
    terraform apply
    ```
    Type `yes` when prompted to confirm the deployment.
    
5. **Access the UI:**
    The Streamlit application is deployed locally for this example. Navigate to `src/streamlit_app/`, update the `OPENSEARCH_HOST` variable with the output from the Terraform apply, and run:
    ```Bash
    pip install -r requirements.txt
    streamlit run app.py
    ```

## Cleanup

To destroy all the resources created by this project, run the following command from the `envs/dev/` directory:
```Bash
terraform destroy
```