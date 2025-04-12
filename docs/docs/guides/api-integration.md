# API Integration Guide

This guide provides detailed examples and best practices for integrating Codex-Arch with your applications and services using our comprehensive API.

## Introduction

The Codex-Arch API allows you to programmatically analyze codebases, extract dependencies, generate visualizations, and build custom architecture analysis workflows. Whether you're building a developer dashboard, integrating with CI/CD pipelines, or creating custom reporting tools, this guide will help you get started.

## Prerequisites

Before integrating with the Codex-Arch API, ensure you have:

1. A Codex-Arch installation (self-hosted or cloud)
2. Authentication credentials (API key, JWT token, or OAuth2 client)
3. Basic knowledge of REST APIs and JSON
4. The appropriate client library or HTTP library for your platform

## Quick Start

Here's a simple example to analyze a codebase and retrieve the results using the API:

```python
# Python example
import requests
import time

API_URL = "https://your-server/api/v1"
API_KEY = "your-api-key"

headers = {
    "Authorization": f"ApiKey {API_KEY}",
    "Content-Type": "application/json"
}

# Step 1: Submit an analysis job
payload = {
    "path": "/path/to/project",
    "exclude": ["node_modules", "*.pyc"],
    "output_format": "json"
}

response = requests.post(f"{API_URL}/analyze", json=payload, headers=headers)
job_data = response.json()
job_id = job_data["job_id"]

# Step 2: Poll for job completion
while True:
    job_status = requests.get(f"{API_URL}/jobs/{job_id}", headers=headers).json()
    if job_status["status"] in ["completed", "failed"]:
        break
    print(f"Job status: {job_status['status']}")
    time.sleep(5)

# Step 3: Retrieve results if job completed successfully
if job_status["status"] == "completed":
    results = requests.get(f"{API_URL}/jobs/{job_id}/result", headers=headers).json()
    print(f"Analysis complete with {len(results['dependencies'])} dependencies found")
```

## Common Integration Scenarios

### 1. Developer Dashboard Integration

Create a dashboard that shows code architecture metrics and visualizations for your team's projects.

```javascript
// JavaScript/Node.js example
const axios = require('axios');

const API_URL = 'https://your-server/api/v1';
const API_KEY = 'your-api-key';

async function getDashboardData(projectId) {
  try {
    // Get project overview
    const overview = await axios.get(`${API_URL}/projects/${projectId}/summary`, {
      headers: { 'Authorization': `ApiKey ${API_KEY}` }
    });
    
    // Get dependency visualization
    const visualization = await axios.post(`${API_URL}/visualize`, {
      job_id: overview.data.last_analysis_job,
      type: 'dependency-graph',
      format: 'svg'
    }, {
      headers: { 
        'Authorization': `ApiKey ${API_KEY}`,
        'Content-Type': 'application/json' 
      }
    });
    
    // Get complexity metrics
    const metrics = await axios.get(`${API_URL}/projects/${projectId}/metrics`, {
      headers: { 'Authorization': `ApiKey ${API_KEY}` }
    });
    
    return {
      overview: overview.data,
      visualization: visualization.data,
      metrics: metrics.data
    };
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    throw error;
  }
}
```

### 2. CI/CD Pipeline Integration

Automatically analyze code during the CI/CD process and fail builds if architecture checks don't pass.

```bash
#!/bin/bash
# Shell script for CI/CD pipeline

# Configure API access
API_URL="https://your-server/api/v1"
API_KEY="your-api-key"

# Submit analysis job
RESPONSE=$(curl -s -X POST "${API_URL}/analyze" \
  -H "Authorization: ApiKey ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"path\": \"${PWD}\",
    \"exclude\": [\"node_modules\", \"*.pyc\"],
    \"async\": true
  }")

JOB_ID=$(echo $RESPONSE | jq -r '.job_id')
echo "Submitted analysis job: ${JOB_ID}"

# Poll for job completion
while true; do
  STATUS=$(curl -s -X GET "${API_URL}/jobs/${JOB_ID}" \
    -H "Authorization: ApiKey ${API_KEY}" | jq -r '.status')
  
  echo "Job status: ${STATUS}"
  
  if [ "${STATUS}" = "completed" ] || [ "${STATUS}" = "failed" ]; then
    break
  fi
  
  sleep 5
done

# Check analysis results
if [ "${STATUS}" = "completed" ]; then
  RESULTS=$(curl -s -X GET "${API_URL}/jobs/${JOB_ID}/result" \
    -H "Authorization: ApiKey ${API_KEY}")
  
  # Check if complexity exceeds threshold
  COMPLEXITY=$(echo $RESULTS | jq '.metrics.complexity.average')
  if (( $(echo "$COMPLEXITY > 15" | bc -l) )); then
    echo "Architecture check failed: Complexity too high (${COMPLEXITY})"
    exit 1
  fi
  
  # Check if dependency count exceeds threshold
  DEP_COUNT=$(echo $RESULTS | jq '.dependencies | length')
  if [ $DEP_COUNT -gt 200 ]; then
    echo "Architecture check failed: Too many dependencies (${DEP_COUNT})"
    exit 1
  fi
  
  echo "Architecture checks passed!"
else
  echo "Analysis failed"
  exit 1
fi
```

### 3. Real-time Monitoring

Create a service that continuously monitors codebase health using webhooks and the Codex-Arch API.

```python
# Python Flask webhook receiver
from flask import Flask, request, jsonify
import hmac
import hashlib
import requests
import json

app = Flask(__name__)

WEBHOOK_SECRET = "your-webhook-secret"
API_URL = "https://your-server/api/v1"
API_KEY = "your-api-key"

def verify_signature(payload_body, signature_header):
    signature = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, signature_header)

@app.route('/webhook/codex-arch', methods=['POST'])
def webhook_receiver():
    # Verify webhook signature
    signature = request.headers.get('X-Codex-Signature')
    if not signature or not verify_signature(request.data, signature):
        return jsonify({"error": "Invalid signature"}), 401
    
    # Process webhook payload
    payload = request.json
    event_type = payload.get('event')
    
    if event_type == 'analysis.significant_change':
        # Alert the team about significant architecture changes
        send_team_alert(payload)
    
    elif event_type == 'analysis.threshold_exceeded':
        # Take action when metrics exceed thresholds
        create_jira_ticket(payload)
    
    return jsonify({"status": "success"}), 200

def send_team_alert(payload):
    # Send Slack notification
    slack_payload = {
        "text": f"⚠️ Significant architecture change detected in {payload['project']}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Significant architecture change detected*\n*Project:* {payload['project']}\n*Changes:* {payload['summary']['changes_summary']}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Details"
                        },
                        "url": f"https://your-dashboard.com/projects/{payload['project']}/changes/{payload['job_id']}"
                    }
                ]
            }
        ]
    }
    
    requests.post("https://hooks.slack.com/services/your/slack/webhook", json=slack_payload)

def create_jira_ticket(payload):
    # Create JIRA ticket for threshold violation
    jira_payload = {
        "fields": {
            "project": {"key": "ARCH"},
            "summary": f"Architecture threshold exceeded in {payload['project']}",
            "description": f"The following metrics exceeded thresholds:\n\n{json.dumps(payload['metrics'], indent=2)}",
            "issuetype": {"name": "Task"},
            "priority": {"name": "High"}
        }
    }
    
    requests.post(
        "https://your-jira-instance/rest/api/2/issue",
        json=jira_payload,
        auth=("jira_username", "jira_password")
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## Best Practices

### Error Handling

Always implement proper error handling in your API integrations:

```python
try:
    response = requests.post(f"{API_URL}/analyze", json=payload, headers=headers)
    response.raise_for_status()  # Raise an exception for 4XX/5XX responses
    job_data = response.json()
except requests.exceptions.RequestException as e:
    print(f"API request failed: {e}")
    # Implement appropriate retry or fallback logic
except ValueError as e:
    print(f"Failed to parse JSON response: {e}")
```

### Rate Limiting

Respect API rate limits and implement backoff strategies:

```python
def api_request_with_backoff(url, method="GET", data=None, max_retries=5):
    headers = {"Authorization": f"ApiKey {API_KEY}"}
    retries = 0
    
    while retries < max_retries:
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            else:
                response = requests.post(url, json=data, headers=headers)
                
            if response.status_code == 429:  # Too Many Requests
                # Get retry-after header or use exponential backoff
                retry_after = int(response.headers.get('Retry-After', 2 ** retries))
                print(f"Rate limited. Retrying after {retry_after} seconds")
                time.sleep(retry_after)
                retries += 1
                continue
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            
            if retries >= max_retries - 1:
                raise
                
            # Exponential backoff with jitter
            sleep_time = (2 ** retries) + random.random()
            print(f"Retrying in {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
            retries += 1
    
    raise Exception("Maximum retries exceeded")
```

### Caching

Cache API responses to improve performance:

```python
import functools
from datetime import datetime, timedelta

# Simple in-memory cache
cache = {}

def cached_api_call(url, expiry_seconds=300):
    if url in cache:
        timestamp, data = cache[url]
        if datetime.now() - timestamp < timedelta(seconds=expiry_seconds):
            print(f"Using cached data for {url}")
            return data
    
    # Cache miss or expired cache
    headers = {"Authorization": f"ApiKey {API_KEY}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    # Update cache
    cache[url] = (datetime.now(), data)
    return data
```

### Security

Follow these security best practices:

1. **Never expose API keys in client-side code**
2. **Use environment variables to store sensitive values**
3. **Implement proper webhook validation**
4. **Apply the principle of least privilege for API tokens**
5. **Always use HTTPS for API requests**

## Advanced Topics

### Batch Processing

For efficient analysis of multiple repositories:

```python
def analyze_multiple_repos(repos):
    # Submit jobs for all repos
    job_ids = []
    for repo in repos:
        payload = {
            "path": repo["path"],
            "output_format": "json",
            "async": True
        }
        response = requests.post(f"{API_URL}/analyze", json=payload, headers=headers)
        job_id = response.json()["job_id"]
        job_ids.append({"repo": repo["name"], "job_id": job_id})
    
    # Poll and collect results
    results = {}
    for job in job_ids:
        # Poll for completion
        while True:
            status = requests.get(f"{API_URL}/jobs/{job['job_id']}", headers=headers).json()
            if status["status"] in ["completed", "failed"]:
                break
            time.sleep(5)
        
        # Collect results
        if status["status"] == "completed":
            result = requests.get(f"{API_URL}/jobs/{job['job_id']}/result", headers=headers).json()
            results[job["repo"]] = result
    
    return results
```

### Streaming Large Results

For very large analysis results:

```python
def download_large_result(job_id, output_file):
    url = f"{API_URL}/jobs/{job_id}/result"
    headers = {"Authorization": f"ApiKey {API_KEY}"}
    
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(output_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    
    print(f"Large result downloaded to {output_file}")
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Ensure your API key or token is valid
   - Check that your token hasn't expired
   - Verify the authorization header format

2. **Rate Limiting**
   - Implement proper backoff and retry logic
   - Consider batching requests when possible
   - Check response headers for rate limit information

3. **Long-Running Jobs**
   - Use asynchronous job submission
   - Implement proper polling with reasonable intervals
   - Consider using webhooks for job completion notifications

### Debugging Tips

1. Enable verbose logging:

```python
import logging
import http.client as http_client

http_client.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
```

2. Inspect response headers:

```python
response = requests.get(f"{API_URL}/status", headers=headers)
print("Response Headers:")
for header, value in response.headers.items():
    print(f"{header}: {value}")
```

## API Client Libraries

Codex-Arch provides official client libraries for several programming languages:

- [Python Client](https://github.com/egouilliard/codex-arch-python-client)
- [JavaScript Client](https://github.com/egouilliard/codex-arch-js-client)
- [Java Client](https://github.com/egouilliard/codex-arch-java-client)

### Python Client Example

```python
from codex_arch_client import CodexArchClient

# Initialize client
client = CodexArchClient(
    base_url="https://your-server/api/v1",
    api_key="your-api-key"
)

# Submit analysis job
job = client.analyze(
    path="/path/to/project",
    exclude=["node_modules", "*.pyc"],
    output_format="json"
)

# Wait for job completion
job.wait_until_complete()

# Get results
if job.is_completed():
    results = job.get_results()
    print(f"Analysis complete with {len(results['dependencies'])} dependencies found")
```

### JavaScript Client Example

```javascript
const { CodexArchClient } = require('codex-arch-client');

// Initialize client
const client = new CodexArchClient({
  baseUrl: 'https://your-server/api/v1',
  apiKey: 'your-api-key'
});

// Submit analysis job and handle with async/await
async function analyzeProject() {
  try {
    const job = await client.analyze({
      path: '/path/to/project',
      exclude: ['node_modules', '*.pyc'],
      outputFormat: 'json'
    });
    
    // Wait for job completion
    await job.waitUntilComplete();
    
    // Get results
    if (job.isCompleted()) {
      const results = await job.getResults();
      console.log(`Analysis complete with ${results.dependencies.length} dependencies found`);
    }
  } catch (error) {
    console.error('Analysis failed:', error);
  }
}

analyzeProject();
```

## Next Steps

- Review the complete [API Endpoints Reference](../api/endpoints.md)
- Learn about [Authentication Methods](../api/authentication.md)
- Explore [External Integration Options](../api/external-integrations.md)
- Set up [Git Hooks Integration](../api/git-hooks.md) 