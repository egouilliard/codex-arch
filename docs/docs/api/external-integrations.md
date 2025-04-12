# External Integration Options

This document outlines the various ways to integrate Codex-Arch with external systems and services, providing flexibility to incorporate code architecture analysis into your existing development workflows.

## Integration Options Overview

Codex-Arch provides multiple integration pathways to fit different development environments and requirements:

| Integration Type | Use Case | Complexity | Setup Time |
|-----------------|----------|------------|------------|
| REST API | Building custom applications or dashboards | Medium | Medium |
| Webhooks | Real-time notifications and triggering external systems | Low | Low |
| CI/CD Pipelines | Automated analysis during build/deployment | Medium | Medium |
| Git Hooks | Automated analysis during Git operations | Low | Low |
| SDK Libraries | Deep integration in custom applications | High | High |
| CLI Integration | Scripting and automation | Low | Low |

## REST API Integration

The Codex-Arch REST API allows deep integration with your applications and services. This is ideal when you need custom workflows or want to incorporate architecture analysis into your own tools.

### Key Features

- Complete access to all analysis capabilities
- Authentication options for different security needs
- Long-running job management
- Webhook notifications for job completion

### Getting Started with REST API

1. [Set up authentication](authentication.md) (API key, JWT, or OAuth2)
2. Review the [API endpoints reference](endpoints.md)
3. Make your first API call:

```bash
# Example: Check API status
curl https://your-server/api/v1/status

# Example: Initiate an analysis
curl -X POST https://your-server/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "path": "/path/to/project",
    "exclude": ["node_modules", "*.pyc"],
    "async": true
  }'
```

### Best Practices

- Cache results when appropriate
- Use asynchronous requests for long-running operations
- Implement proper error handling
- Apply rate limiting in high-volume scenarios

## Webhooks Integration

Webhooks provide a way for Codex-Arch to notify your systems when events occur, such as when analysis jobs complete or significant architecture changes are detected.

### Supported Events

- `job.created` - A new analysis job is created
- `job.completed` - An analysis job has completed
- `job.failed` - An analysis job has failed
- `analysis.significant_change` - Significant architecture changes detected
- `analysis.threshold_exceeded` - Complexity or other metrics exceeded thresholds

### Webhook Payload Example

```json
{
  "event": "job.completed",
  "timestamp": "2023-01-01T12:00:00Z",
  "job_id": "abc123",
  "status": "completed",
  "project": "my-project",
  "results_url": "/api/v1/jobs/abc123/result",
  "summary": {
    "files_analyzed": 250,
    "warnings": 5,
    "errors": 0
  }
}
```

### Setting Up Webhooks

1. Create a webhook endpoint in your application
2. Register the webhook with Codex-Arch:

```bash
curl -X POST https://your-server/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "url": "https://your-app.com/webhooks/codex-arch",
    "events": ["job.completed", "analysis.significant_change"],
    "name": "Architecture Analysis Notifications",
    "secret": "your-webhook-secret"
  }'
```

3. Implement webhook signature verification for security:

```python
# Python example
import hmac
import hashlib

def verify_webhook(request_body, signature_header, webhook_secret):
    signature = hmac.new(
        webhook_secret.encode('utf-8'),
        request_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, signature_header)
```

## CI/CD Pipeline Integration

Integrate Codex-Arch into your CI/CD pipelines to analyze architecture changes before deployment.

### GitHub Actions Integration

Create a file at `.github/workflows/codex-arch-analysis.yml`:

```yaml
name: Codex-Arch Analysis

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for change analysis
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install Codex-Arch
        run: pip install codex-arch
      
      - name: Run Architecture Analysis
        run: |
          codex-arch analyze \
            --path . \
            --exclude "node_modules,*.pyc" \
            --output-format json \
            --output-file arch-analysis.json
        env:
          CODEX_ARCH_API_KEY: ${{ secrets.CODEX_ARCH_API_KEY }}
      
      - name: Check Analysis Results
        run: |
          python .github/scripts/check_analysis_results.py
      
      - name: Upload Analysis Results
        uses: actions/upload-artifact@v3
        with:
          name: architecture-analysis
          path: arch-analysis.json
```

### GitLab CI Integration

Create a `.gitlab-ci.yml` file:

```yaml
stages:
  - test
  - analyze

architecture-analysis:
  stage: analyze
  image: python:3.10
  script:
    - pip install codex-arch
    - codex-arch analyze --path . --output-format json --output-file arch-analysis.json
    - python scripts/check_analysis_results.py
  artifacts:
    paths:
      - arch-analysis.json
    expire_in: 1 week
  only:
    - main
    - merge_requests
```

### Jenkins Pipeline Integration

```groovy
pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh 'pip install codex-arch'
            }
        }
        
        stage('Architecture Analysis') {
            steps {
                sh '''
                codex-arch analyze \
                  --path . \
                  --exclude "node_modules,*.pyc" \
                  --output-format json \
                  --output-file arch-analysis.json
                '''
            }
        }
        
        stage('Review Analysis') {
            steps {
                sh 'python scripts/check_analysis_results.py'
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'arch-analysis.json', fingerprint: true
        }
    }
}
```

## Git Hooks Integration

Git hooks provide a way to trigger architecture analysis during Git operations. See our detailed [Git hooks documentation](git-hooks.md) for full implementation details.

### Quick Start

```bash
# Install Codex-Arch Git hooks
codex-arch hooks install

# Configure hooks (creates .codex-arch-hooks.json)
codex-arch hooks configure
```

## SDK Libraries Integration

For deep integration into your applications, use our official SDK libraries.

### Python SDK

```bash
pip install codex-arch-sdk
```

```python
from codex_arch_sdk import CodexArchClient

# Initialize client
client = CodexArchClient(api_key="your-api-key")

# Start an analysis
job = client.analyze(
    path="/path/to/project",
    exclude=["node_modules", "*.pyc"],
    async_execution=True
)

# Check job status
status = client.get_job_status(job.job_id)

# Get results when complete
if status.is_complete:
    results = client.get_job_results(job.job_id)
    print(f"Files analyzed: {results.summary.files_analyzed}")
    print(f"Architecture score: {results.metrics.architecture_score}")
```

### JavaScript/TypeScript SDK

```bash
npm install codex-arch-sdk
# or
yarn add codex-arch-sdk
```

```javascript
import { CodexArchClient } from 'codex-arch-sdk';

// Initialize client
const client = new CodexArchClient({
  apiKey: 'your-api-key'
});

// Start an analysis
async function runAnalysis() {
  try {
    const job = await client.analyze({
      path: '/path/to/project',
      exclude: ['node_modules', '*.pyc'],
      asyncExecution: true
    });
    
    // Poll for completion
    const checkStatus = async () => {
      const status = await client.getJobStatus(job.jobId);
      
      if (status.isComplete) {
        const results = await client.getJobResults(job.jobId);
        console.log(`Files analyzed: ${results.summary.filesAnalyzed}`);
        console.log(`Architecture score: ${results.metrics.architectureScore}`);
      } else {
        setTimeout(checkStatus, 5000);
      }
    };
    
    checkStatus();
  } catch (error) {
    console.error('Analysis failed:', error);
  }
}

runAnalysis();
```

## CLI Integration

The Codex-Arch CLI tool can be easily incorporated into scripts and automation workflows.

### Simple Script Example

```bash
#!/bin/bash

# Run analysis and save results
codex-arch analyze --path ./my-project --output-format json --output-file results.json

# Check for specific issues
if grep -q "circular_dependency" results.json; then
  echo "Error: Circular dependencies detected!"
  exit 1
fi

# Generate and save visualization
codex-arch visualize --input results.json --type dependency-graph --output arch-diagram.svg

# Success
echo "Architecture analysis completed successfully"
exit 0
```

### Advanced Script with Comparison

```bash
#!/bin/bash

# Get current branch name
BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Run analysis on current branch
codex-arch analyze --path . --output-format json --output-file current-analysis.json

# Checkout main branch and analyze
git checkout main
codex-arch analyze --path . --output-format json --output-file main-analysis.json

# Return to original branch
git checkout $BRANCH

# Compare the two analyses
codex-arch compare --base main-analysis.json --target current-analysis.json --output-format markdown --output-file comparison.md

# Clean up
rm main-analysis.json

echo "Analysis comparison saved to comparison.md"
```

## Monitoring and Data Collection Integration

For teams that want to track architecture trends over time, you can integrate Codex-Arch with monitoring systems.

### Prometheus Integration Example

1. Enable the metrics endpoint in your Codex-Arch configuration.
2. Configure Prometheus to scrape the `/metrics` endpoint.
3. Create dashboards to visualize architecture trends.

Sample Prometheus configuration:

```yaml
scrape_configs:
  - job_name: 'codex-arch'
    scrape_interval: 1m
    static_configs:
      - targets: ['codex-arch-server:9090']
```

### Custom Data Pipeline Example

This Python script shows how to extract analysis results and push them to a data warehouse:

```python
import requests
import pandas as pd
from sqlalchemy import create_engine
import json
from datetime import datetime

# Configuration
CODEX_ARCH_URL = "https://your-server/api/v1"
API_KEY = "your-api-key"
DB_CONNECTION = "postgresql://user:password@localhost:5432/metrics_db"

# Get latest analysis results
headers = {"Authorization": f"Bearer {API_KEY}"}
response = requests.get(f"{CODEX_ARCH_URL}/jobs?status=completed&limit=1", headers=headers)
latest_job = response.json()["jobs"][0]

# Get detailed results
results_response = requests.get(
    f"{CODEX_ARCH_URL}/jobs/{latest_job['job_id']}/result", 
    headers=headers
)
results = results_response.json()

# Extract metrics for database storage
metrics = []
timestamp = datetime.now().isoformat()

# Extract file metrics
for file_path, file_data in results["files"].items():
    metrics.append({
        "timestamp": timestamp,
        "file_path": file_path,
        "loc": file_data.get("loc", 0),
        "complexity": file_data.get("complexity", 0),
        "dependencies": len(file_data.get("dependencies", [])),
        "commit_id": latest_job.get("commit_id", "unknown")
    })

# Store in database
df = pd.DataFrame(metrics)
engine = create_engine(DB_CONNECTION)
df.to_sql("architecture_metrics", engine, if_exists="append", index=False)

print(f"Stored metrics for {len(metrics)} files")
```

## Security Considerations

When integrating Codex-Arch with external systems, consider these security best practices:

1. **Access Management**:
   - Use scoped API keys with minimal permissions
   - Rotate API keys regularly
   - Use OAuth2 for user-based integrations

2. **Data Protection**:
   - Encrypt sensitive data in transit and at rest
   - Be mindful of what information is shared in webhooks
   - Configure proper access controls on visualization outputs

3. **System Security**:
   - Run integrations in isolated environments
   - Implement proper input validation
   - Maintain updated dependencies

4. **Audit and Monitoring**:
   - Log all API access and activities
   - Set up alerts for unusual activity
   - Regularly review webhook endpoints

## Troubleshooting Integration Issues

### Common Issues and Solutions

1. **Authentication Failures**
   - Check that your API key or token is valid and not expired
   - Ensure you're using the correct authentication header format

2. **Webhook Delivery Problems**
   - Verify your webhook URL is publicly accessible
   - Check for firewall or network restrictions
   - Enable webhook logs for debugging

3. **CI/CD Integration Issues**
   - Ensure environment variables are properly set
   - Check for permission issues in your CI environment
   - Verify paths are correct for your CI environment

4. **Rate Limiting**
   - Implement exponential backoff for retries
   - Cache results where appropriate
   - Distribute requests over time

### Debugging Tools

- Enable debug mode in SDK libraries:
  ```python
  client = CodexArchClient(api_key="your-api-key", debug=True)
  ```

- Use webhook testing tools:
  ```bash
  codex-arch webhooks test --webhook-id wh123
  ```

- Verify API connectivity:
  ```bash
  curl -v https://your-server/api/v1/status
  ```

## Next Steps

- Review the [Authentication documentation](authentication.md) for securing your integrations
- Check the [API Endpoints Reference](endpoints.md) for detailed API capabilities
- See the [Git Hooks documentation](git-hooks.md) for Git-based automation
- Join our community forums to share integration tips and questions 