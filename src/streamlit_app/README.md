# Streamlit App Setup Guide

## Quick Start

1. **Copy Environment File**:
   ```bash
   cp .env.example .env
   ```

2. **Configure OpenSearch Endpoint**:
   - Deploy your Terraform infrastructure first
   - Get the OpenSearch endpoint:
     ```bash
     cd ../../envs/dev  # or prod
     terraform output opensearch_collection_endpoint
     ```
   - Update `OPENSEARCH_HOST` in your `.env` file

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure AWS Credentials**:
   ```bash
   aws configure
   # OR use IAM roles in production
   ```

5. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## Configuration Options

### Environment-Specific Settings

**Development**:
```env
LOG_LEVEL=DEBUG
ENABLE_DEBUG_MODE=true
MAX_TOKENS_PER_SESSION=100000
DEFAULT_SEARCH_SIZE=5
```

**Production**:
```env
LOG_LEVEL=INFO
ENABLE_DEBUG_MODE=false
MAX_TOKENS_PER_SESSION=1000000
DEFAULT_SEARCH_SIZE=15
```

### Alternative: Streamlit Secrets

Instead of `.env`, you can use Streamlit's secrets management:

1. Create `.streamlit/secrets.toml`:
   ```toml
   AWS_REGION = "us-east-1"
   OPENSEARCH_HOST = "your-endpoint.aoss.amazonaws.com"
   # ... other variables
   ```

2. The app will automatically use secrets if environment variables aren't set

## Troubleshooting

### Common Issues

1. **"Configuration errors detected"**:
   - Check that `OPENSEARCH_HOST` is set correctly
   - Verify AWS credentials are configured

2. **"AWS credentials not found"**:
   - Run `aws configure`
   - Or ensure IAM roles are properly attached

3. **"Bedrock API error"**:
   - Check that Bedrock models are available in your region
   - Verify IAM permissions for Bedrock access

4. **"Rate limit exceeded"**:
   - Adjust `MAX_REQUESTS_PER_HOUR` in configuration
   - Wait for rate limit to reset

### Debug Mode

Enable debug mode for troubleshooting:
```env
ENABLE_DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

This will show additional information in the sidebar and logs.

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### AWS ECS/Fargate
- Set environment variables in task definition
- Use IAM roles for AWS authentication
- Configure security groups for port 8501

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: streamlit-logs
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: app
        image: your-registry/streamlit-logs:latest
        ports:
        - containerPort: 8501
        envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: app-secrets
```

## Security Best Practices

1. **Never commit `.env` files**
2. **Use IAM roles in production**
3. **Rotate credentials regularly**
4. **Set appropriate rate limits**
5. **Monitor cost metrics**
6. **Use HTTPS in production**
7. **Implement proper logging**

## Monitoring

The app provides built-in monitoring via:
- Cost tracking in sidebar
- Usage metrics display
- Structured logging
- Performance timing

Monitor these metrics to optimize performance and costs.