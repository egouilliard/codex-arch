# API Module

The API module provides a RESTful interface to Codex-Arch functionality, enabling integration with external systems, web applications, and development workflows.

## Overview

The API module offers HTTP endpoints to:

- Trigger codebase analysis
- Retrieve analysis results
- Query specific metrics and dependencies
- Generate visualizations
- Manage analysis configurations

The API service is built with FastAPI, providing automatic documentation, request validation, and powerful routing capabilities.

## Module Structure

```
api/
├── __init__.py         # Package exports
├── app.py              # FastAPI application setup
├── server.py           # Server configuration and startup
├── routes/             # API route definitions
│   ├── __init__.py     # Routes exports
│   ├── analysis.py     # Analysis endpoints
│   ├── dependencies.py # Dependency-related endpoints
│   ├── metrics.py      # Metrics endpoints
│   ├── visualizations.py # Visualization endpoints
│   └── config.py       # Configuration endpoints
├── middleware/         # API middleware components
│   ├── __init__.py     # Middleware exports
│   ├── auth.py         # Authentication middleware
│   ├── logging.py      # Request logging middleware
│   └── cache.py        # Response caching middleware
├── models/             # API data models
│   ├── __init__.py     # Models exports
│   ├── requests.py     # Request data models
│   └── responses.py    # Response data models
└── utils/              # API utilities
    ├── __init__.py     # Utilities exports
    ├── validation.py   # Input validation utilities
    └── formatting.py   # Response formatting utilities
```

## Key Components

### API Application

The main FastAPI application that sets up the API server.

```python
from codex_arch.api import create_app

# Create the API application with default settings
app = create_app()

# Create the API application with custom settings
app = create_app(
    title="Custom Codex-Arch API",
    description="A custom API for Codex-Arch",
    version="1.2.0",
    debug=True,
    enable_cors=True,
    enable_authentication=True,
    enable_rate_limiting=True
)

# Run the API server
from codex_arch.api import run_server
run_server(app, host="0.0.0.0", port=8000)
```

#### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `title` | API title shown in documentation | `"Codex-Arch API"` |
| `description` | API description | `"RESTful API for Codex-Arch code architecture analysis"` |
| `version` | API version | `"1.0.0"` |
| `debug` | Enable debug mode | `False` |
| `enable_cors` | Enable CORS support | `True` |
| `enable_authentication` | Enable authentication | `True` |
| `enable_rate_limiting` | Enable rate limiting | `True` |
| `rate_limit_requests` | Maximum requests per minute | `60` |
| `cache_enabled` | Enable response caching | `True` |
| `cache_ttl` | Cache time-to-live in seconds | `300` |

### Authentication

The API supports multiple authentication methods:

```python
from codex_arch.api import create_app, AuthType

# Create app with API key authentication
app = create_app(
    auth_type=AuthType.API_KEY,
    api_keys=["your-secret-key-1", "your-secret-key-2"]
)

# Create app with OAuth2 authentication
app = create_app(
    auth_type=AuthType.OAUTH2,
    oauth2_config={
        "token_url": "/token",
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "scopes": {
            "read:analysis": "Read analysis results",
            "write:analysis": "Create and update analysis"
        }
    }
)

# Create app with JWT authentication
app = create_app(
    auth_type=AuthType.JWT,
    jwt_secret="your-jwt-secret-key",
    jwt_algorithm="HS256",
    jwt_expires_minutes=30
)
```

### Analysis Endpoints

The core endpoints for triggering and retrieving analysis results:

```python
import requests

# Start a new analysis
response = requests.post(
    "http://localhost:8000/api/v1/analysis",
    headers={"Authorization": "Bearer your-token"},
    json={
        "repository_path": "/path/to/repository",
        "include_patterns": ["*.py", "*.js"],
        "exclude_patterns": ["**/node_modules/**", "**/__pycache__/**"],
        "analysis_depth": 3,
        "include_metrics": True,
        "include_dependencies": True,
        "output_format": "json"
    }
)
analysis_id = response.json()["analysis_id"]

# Check analysis status
status_response = requests.get(
    f"http://localhost:8000/api/v1/analysis/{analysis_id}/status",
    headers={"Authorization": "Bearer your-token"}
)
status = status_response.json()["status"]  # "pending", "running", "completed", "failed"

# Get analysis results
results_response = requests.get(
    f"http://localhost:8000/api/v1/analysis/{analysis_id}/results",
    headers={"Authorization": "Bearer your-token"}
)
results = results_response.json()
```

### Metrics Endpoints

Endpoints for retrieving specific metrics:

```python
import requests

# Get all metrics for a completed analysis
metrics_response = requests.get(
    f"http://localhost:8000/api/v1/analysis/{analysis_id}/metrics",
    headers={"Authorization": "Bearer your-token"}
)
all_metrics = metrics_response.json()

# Get specific metrics
complexity_metrics = requests.get(
    f"http://localhost:8000/api/v1/analysis/{analysis_id}/metrics/complexity",
    headers={"Authorization": "Bearer your-token"}
)

# Get metrics for a specific file or module
file_metrics = requests.get(
    f"http://localhost:8000/api/v1/analysis/{analysis_id}/metrics",
    headers={"Authorization": "Bearer your-token"},
    params={"path": "src/module/file.py"}
)
```

### Dependency Endpoints

Endpoints for retrieving dependency information:

```python
import requests

# Get all dependencies
deps_response = requests.get(
    f"http://localhost:8000/api/v1/analysis/{analysis_id}/dependencies",
    headers={"Authorization": "Bearer your-token"}
)
all_dependencies = deps_response.json()

# Get dependencies for a specific module
module_deps = requests.get(
    f"http://localhost:8000/api/v1/analysis/{analysis_id}/dependencies",
    headers={"Authorization": "Bearer your-token"},
    params={"module": "src.module"}
)

# Get dependency graph
graph_response = requests.get(
    f"http://localhost:8000/api/v1/analysis/{analysis_id}/dependencies/graph",
    headers={"Authorization": "Bearer your-token"},
    params={"format": "dot"}
)
```

### Visualization Endpoints

Endpoints for generating visualizations:

```python
import requests

# Generate a dependency graph visualization
vis_response = requests.get(
    f"http://localhost:8000/api/v1/analysis/{analysis_id}/visualizations/dependency-graph",
    headers={"Authorization": "Bearer your-token"},
    params={
        "format": "svg",
        "direction": "LR",
        "cluster_by_package": "true"
    }
)
with open("dependency-graph.svg", "wb") as f:
    f.write(vis_response.content)

# Generate a metrics visualization
metrics_vis = requests.get(
    f"http://localhost:8000/api/v1/analysis/{analysis_id}/visualizations/metrics",
    headers={"Authorization": "Bearer your-token"},
    params={
        "chart_type": "bar",
        "metrics": "complexity,loc,dependencies",
        "top_n": "10",
        "format": "png"
    }
)
with open("metrics-chart.png", "wb") as f:
    f.write(metrics_vis.content)
```

## Integration Examples

### Python Client Integration

```python
from codex_arch.api.client import CodexArchClient

# Create a client instance
client = CodexArchClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Start an analysis
analysis_id = client.start_analysis(
    repository_path="/path/to/repository",
    include_patterns=["*.py", "*.js"],
    exclude_patterns=["**/node_modules/**"],
)

# Wait for analysis to complete
client.wait_for_analysis(analysis_id, timeout=300)

# Get results
results = client.get_analysis_results(analysis_id)

# Get specific metrics
complexity = client.get_metrics(analysis_id, metric_type="complexity")
loc = client.get_metrics(analysis_id, metric_type="loc")

# Get dependencies
dependencies = client.get_dependencies(analysis_id)

# Generate and save a visualization
client.get_visualization(
    analysis_id, 
    vis_type="dependency-graph",
    output_path="dependency-graph.svg",
    params={"format": "svg", "direction": "LR"}
)
```

### Web Integration Example

```javascript
// Example using fetch in JavaScript
async function runAnalysis() {
  // Start the analysis
  const startResponse = await fetch('http://localhost:8000/api/v1/analysis', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer your-token'
    },
    body: JSON.stringify({
      repository_path: '/path/to/repository',
      include_patterns: ['*.py', '*.js'],
      exclude_patterns: ['**/node_modules/**', '**/__pycache__/**']
    })
  });
  
  const { analysis_id } = await startResponse.json();
  
  // Poll for status until complete
  let status = 'pending';
  while (status !== 'completed' && status !== 'failed') {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const statusResponse = await fetch(`http://localhost:8000/api/v1/analysis/${analysis_id}/status`, {
      headers: { 'Authorization': 'Bearer your-token' }
    });
    
    const statusData = await statusResponse.json();
    status = statusData.status;
  }
  
  if (status === 'failed') {
    console.error('Analysis failed');
    return;
  }
  
  // Get the results
  const resultsResponse = await fetch(`http://localhost:8000/api/v1/analysis/${analysis_id}/results`, {
    headers: { 'Authorization': 'Bearer your-token' }
  });
  
  const results = await resultsResponse.json();
  console.log('Analysis results:', results);
  
  // Get dependency graph visualization
  const visResponse = await fetch(
    `http://localhost:8000/api/v1/analysis/${analysis_id}/visualizations/dependency-graph?format=svg`, 
    { headers: { 'Authorization': 'Bearer your-token' } }
  );
  
  const svgData = await visResponse.text();
  document.getElementById('visualization-container').innerHTML = svgData;
}
```

## API Reference

For a complete list of all available endpoints, parameters, and response formats, see the auto-generated [API Reference](../api/rest-api.md).

### OpenAPI Specification

When running the API server, the OpenAPI specification is available at `/docs` or `/openapi.json`. This can be used with tools like Swagger UI or Postman for API exploration.

## Authentication Methods

### API Key Authentication

```python
# Using the requests library
import requests

headers = {"X-API-Key": "your-api-key"}
response = requests.get("http://localhost:8000/api/v1/analysis", headers=headers)
```

### JWT Authentication

```python
# First, get a token
import requests

token_response = requests.post(
    "http://localhost:8000/api/v1/auth/token",
    json={"username": "your-username", "password": "your-password"}
)
token = token_response.json()["access_token"]

# Then use the token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/api/v1/analysis", headers=headers)
```

### OAuth2 Authentication

```python
# Using the requests-oauthlib library
from requests_oauthlib import OAuth2Session

client_id = "your-client-id"
client_secret = "your-client-secret"
token_url = "http://localhost:8000/api/v1/auth/token"

oauth = OAuth2Session(client_id)
token = oauth.fetch_token(
    token_url=token_url,
    client_id=client_id,
    client_secret=client_secret,
    username="your-username",
    password="your-password"
)

# Make authenticated requests
response = oauth.get("http://localhost:8000/api/v1/analysis")
```

## Rate Limiting

The API implements rate limiting to prevent abuse:

- By default, clients are limited to 60 requests per minute
- Rate limits can be customized per client
- Rate limit headers are included in responses:
  - `X-RateLimit-Limit`: Maximum requests allowed per minute
  - `X-RateLimit-Remaining`: Remaining requests in the current window
  - `X-RateLimit-Reset`: Seconds until the rate limit resets

When a rate limit is exceeded, the API returns a 429 Too Many Requests response.

## Error Handling

The API uses standard HTTP status codes and provides detailed error messages:

```json
{
  "status": "error",
  "code": "invalid_repository_path",
  "message": "The provided repository path does not exist or is not accessible",
  "details": {
    "path": "/path/to/nonexistent/repository"
  }
}
```

Common error codes include:

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | `invalid_request` | The request is malformed or contains invalid parameters |
| 401 | `unauthorized` | Authentication is required or credentials are invalid |
| 403 | `forbidden` | The authenticated user doesn't have access to the requested resource |
| 404 | `not_found` | The requested resource doesn't exist |
| 429 | `rate_limit_exceeded` | The client has exceeded the rate limit |
| 500 | `internal_error` | An unexpected server error occurred |

## Relevant Files

The main implementation files for the API module:

- `codex_arch/api/__init__.py`: Package exports
- `codex_arch/api/app.py`: FastAPI application setup
- `codex_arch/api/server.py`: Server configuration and startup
- `codex_arch/api/routes/`: API route definitions
- `codex_arch/api/middleware/`: API middleware components
- `codex_arch/api/models/`: API data models
- `codex_arch/api/utils/`: API utilities

## Configuration Examples

### Example 1: Basic API Server Configuration

```python
# config.py
api_config = {
    "title": "Codex-Arch API",
    "description": "Code architecture analysis API",
    "version": "1.0.0",
    "host": "0.0.0.0",
    "port": 8000,
    "debug": False,
    "enable_cors": True,
    "cors_origins": ["http://localhost:3000", "https://your-app.com"],
    "enable_authentication": True,
    "auth_type": "api_key",
    "api_keys": ["your-secret-key"],
    "enable_rate_limiting": True,
    "rate_limit_requests": 60,
    "cache_enabled": True,
    "cache_ttl": 300
}

# server.py
from codex_arch.api import create_app, run_server
from config import api_config

app = create_app(**api_config)

if __name__ == "__main__":
    run_server(app, host=api_config["host"], port=api_config["port"])
```

### Example 2: API Configuration in YAML Format

```yaml
# api-config.yml
api:
  title: "Codex-Arch API"
  description: "Code architecture analysis API"
  version: "1.0.0"
  host: "0.0.0.0"
  port: 8000
  debug: false
  
  cors:
    enabled: true
    origins:
      - "http://localhost:3000"
      - "https://your-app.com"
      
  authentication:
    enabled: true
    type: "jwt"  # api_key, jwt, oauth2
    jwt_secret: "your-jwt-secret-key"
    jwt_algorithm: "HS256"
    jwt_expires_minutes: 30
    
  rate_limiting:
    enabled: true
    requests_per_minute: 60
    
  caching:
    enabled: true
    ttl_seconds: 300
```

```python
# server.py
import yaml
from codex_arch.api import create_app, run_server

# Load configuration from YAML
with open("api-config.yml", "r") as f:
    config = yaml.safe_load(f)["api"]

# Create and run the app
app = create_app(
    title=config["title"],
    description=config["description"],
    version=config["version"],
    debug=config["debug"],
    enable_cors=config["cors"]["enabled"],
    cors_origins=config["cors"]["origins"],
    enable_authentication=config["authentication"]["enabled"],
    auth_type=config["authentication"]["type"],
    jwt_secret=config["authentication"].get("jwt_secret"),
    jwt_algorithm=config["authentication"].get("jwt_algorithm"),
    jwt_expires_minutes=config["authentication"].get("jwt_expires_minutes"),
    enable_rate_limiting=config["rate_limiting"]["enabled"],
    rate_limit_requests=config["rate_limiting"]["requests_per_minute"],
    cache_enabled=config["caching"]["enabled"],
    cache_ttl=config["caching"]["ttl_seconds"]
)

if __name__ == "__main__":
    run_server(app, host=config["host"], port=config["port"])
```

### Example 3: Using the API Server from Command Line

```bash
# Start the API server with default settings
codex-arch api start

# Start the API server with custom settings
codex-arch api start --host 0.0.0.0 --port 8000 --auth-type api_key --api-key your-secret-key

# Start the API server with a configuration file
codex-arch api start --config api-config.yml
```

## Best Practices

- **Security**:
  - Always enable authentication in production
  - Use HTTPS in production environments
  - Regularly rotate API keys and secrets
  - Implement proper access control for sensitive operations

- **Performance**:
  - Enable caching for frequently accessed resources
  - Use pagination for endpoints that return large collections
  - Implement background processing for long-running operations

- **Integration**:
  - Use the client library for easier integration
  - Handle rate limiting gracefully with backoff strategies
  - Implement proper error handling in client applications
  - Set reasonable timeouts for API requests

- **Monitoring**:
  - Log API errors and monitor error rates
  - Track API usage and performance metrics
  - Set up alerts for API availability and error thresholds 