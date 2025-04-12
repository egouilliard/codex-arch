# REST API Reference

Codex-Arch provides a REST API that allows you to access all functionality programmatically. This document describes the API endpoints, authentication mechanisms, and includes examples for common operations.

## API Overview

The REST API allows you to:

- Analyze codebases
- Extract dependencies
- Generate visualizations
- Retrieve metrics
- Create summary reports
- Monitor changes over time

## Getting Started

### Starting the API Server

To start the API server:

```bash
codex-arch api serve --host=0.0.0.0 --port=5000
```

By default, the server will run on `localhost:5000`.

### Authentication

The API supports multiple authentication methods:

#### API Key Authentication

For simple integrations, you can use API key authentication:

```bash
# Set your API key
export CODEX_ARCH_API_KEY=your-api-key

# Use in requests
curl -H "X-Api-Key: your-api-key" http://localhost:5000/api/v1/status
```

#### JWT Authentication

For more secure environments, JWT authentication is supported:

```bash
# Obtain a token
curl -X POST http://localhost:5000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "your-username", "password": "your-password"}'

# Use the token in requests
curl -H "Authorization: Bearer your-jwt-token" http://localhost:5000/api/v1/status
```

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/status` | GET | Get API server status |
| `/api/v1/analyze` | POST | Analyze a codebase |
| `/api/v1/extract` | POST | Extract information from a codebase |
| `/api/v1/visualize` | POST | Generate visualizations |
| `/api/v1/metrics` | POST | Calculate metrics |
| `/api/v1/summary` | POST | Generate summary |
| `/api/v1/changes` | POST | Analyze changes |

### Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/token` | POST | Obtain JWT token |
| `/api/v1/auth/refresh` | POST | Refresh JWT token |
| `/api/v1/auth/revoke` | POST | Revoke JWT token |

## Detailed Endpoint Documentation

### Status Endpoint

**Endpoint:** `/api/v1/status`  
**Method:** GET  
**Description:** Get the current status of the API server.

**Example Request:**
```bash
curl http://localhost:5000/api/v1/status
```

**Example Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime": "3h 24m 12s",
  "memory_usage": "128MB"
}
```

### Analyze Endpoint

**Endpoint:** `/api/v1/analyze`  
**Method:** POST  
**Description:** Analyze a codebase and return comprehensive results.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Path to the codebase to analyze |
| `exclude` | array | No | Patterns to exclude |
| `include` | array | No | Patterns to include |
| `max_depth` | integer | No | Maximum directory depth |
| `output_format` | string | No | Format of results (`json`, `markdown`, `html`) |

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "path": "/path/to/project",
    "exclude": ["node_modules", "*.pyc"],
    "output_format": "json"
  }'
```

**Example Response:**
```json
{
  "job_id": "abc123",
  "status": "processing",
  "results_url": "/api/v1/jobs/abc123",
  "estimated_time": "30s"
}
```

### Extract Endpoint

**Endpoint:** `/api/v1/extract`  
**Method:** POST  
**Description:** Extract specific information from a codebase.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Path to the codebase to analyze |
| `extractors` | array | Yes | List of extractors to use |
| `exclude` | array | No | Patterns to exclude |
| `output_format` | string | No | Format of results (`json`, `markdown`, `html`) |

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/v1/extract \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "path": "/path/to/project",
    "extractors": ["file-tree", "python-deps"],
    "exclude": ["node_modules", "*.pyc"],
    "output_format": "json"
  }'
```

**Example Response:**
```json
{
  "job_id": "def456",
  "status": "processing",
  "results_url": "/api/v1/jobs/def456",
  "estimated_time": "15s"
}
```

### Visualize Endpoint

**Endpoint:** `/api/v1/visualize`  
**Method:** POST  
**Description:** Generate visualizations from analysis results.

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `data` | object | Yes* | Analysis data to visualize |
| `job_id` | string | Yes* | ID of a completed analysis job |
| `type` | string | Yes | Type of visualization (`dependency-graph`, `treemap`, `sunburst`) |
| `format` | string | No | Output format (`svg`, `png`, `pdf`, default: `svg`) |
| `options` | object | No | Visualization-specific options |

\* Either `data` or `job_id` must be provided

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/v1/visualize \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "job_id": "abc123",
    "type": "dependency-graph",
    "format": "svg",
    "options": {
      "group_by": "package",
      "include_external": false
    }
  }'
```

**Example Response:**
```json
{
  "job_id": "ghi789",
  "status": "completed",
  "result": {
    "image_url": "/api/v1/jobs/ghi789/result",
    "format": "svg"
  }
}
```

## Working with Jobs

Many API endpoints create asynchronous jobs. You can check the status of a job and retrieve results using the jobs API:

### Get Job Status

**Endpoint:** `/api/v1/jobs/{job_id}`  
**Method:** GET  
**Description:** Get the status of a job.

**Example Request:**
```bash
curl http://localhost:5000/api/v1/jobs/abc123 \
  -H "Authorization: Bearer your-jwt-token"
```

**Example Response:**
```json
{
  "job_id": "abc123",
  "status": "completed",
  "created_at": "2023-01-01T12:00:00Z",
  "completed_at": "2023-01-01T12:01:30Z",
  "results_url": "/api/v1/jobs/abc123/result"
}
```

### Get Job Result

**Endpoint:** `/api/v1/jobs/{job_id}/result`  
**Method:** GET  
**Description:** Get the result of a completed job.

**Example Request:**
```bash
curl http://localhost:5000/api/v1/jobs/abc123/result \
  -H "Authorization: Bearer your-jwt-token"
```

The response will contain the result of the job, which can be JSON data, an image file, or other formats depending on the job type.

## Error Handling

The API uses standard HTTP status codes to indicate success or failure of requests:

- `200 OK`: The request was successful
- `201 Created`: A resource was successfully created
- `202 Accepted`: The request was accepted for processing
- `400 Bad Request`: The request was invalid
- `401 Unauthorized`: Authentication is required
- `403 Forbidden`: The authenticated user doesn't have permission
- `404 Not Found`: The requested resource doesn't exist
- `500 Server Error`: An error occurred on the server

Error responses include a JSON body with details:

```json
{
  "error": "Bad Request",
  "code": "INVALID_PARAMETER",
  "message": "The 'path' parameter is required",
  "details": {
    "parameter": "path",
    "reason": "missing"
  }
}
```

## API Versioning

The API is versioned using the URL path (e.g., `/api/v1/...`). When breaking changes are introduced, a new version will be released.

## Rate Limiting

The API includes rate limiting to prevent abuse:

- 60 requests per minute for authenticated users
- 5 requests per minute for unauthenticated users

Rate limit information is included in response headers:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1640995200
```

## SDKs and Client Libraries

Official client libraries are available for several languages:

- [Python Client](https://github.com/egouilliard/codex-arch-python-client)
- [JavaScript Client](https://github.com/egouilliard/codex-arch-js-client)
- [Java Client](https://github.com/egouilliard/codex-arch-java-client)

## API Changelog

### v1.0.0 (2023-01-01)

- Initial release of the API
- Support for analyzing codebases
- Support for extracting dependencies
- Support for generating visualizations

## Next Steps

For more advanced usage, see:

- [API Integration Guide](../guides/api-integration.md) for examples of using the API in different scenarios
- [Authentication Guide](authentication.md) for detailed information about authentication options
- [Endpoints Reference](endpoints.md) for a complete list of all endpoints 