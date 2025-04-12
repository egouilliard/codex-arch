# API Endpoints Reference

This document provides a complete reference for all Codex-Arch API endpoints, with detailed parameter descriptions and usage examples.

## Core API Structure

The Codex-Arch API follows RESTful principles with predictable URL structures:

- Base URL: `https://your-server/api/v1/`
- Resources are organized by functionality
- HTTP methods indicate the action to be performed
- Response formats are primarily JSON
- Error handling is consistent across endpoints

## Status Endpoints

### Get API Status

Returns the current status of the API server, including version and health information.

**Endpoint:** `/api/v1/status`  
**Method:** GET  
**Authentication:** Optional  

**Example Request:**
```bash
curl https://your-server/api/v1/status
```

**Example Response (200 OK):**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime": "3h 24m 12s",
  "memory_usage": "128MB",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "storage": "healthy"
  }
}
```

## Analysis Endpoints

### Submit Analysis Job

Initiates a codebase analysis job.

**Endpoint:** `/api/v1/analyze`  
**Method:** POST  
**Authentication:** Required  
**Content-Type:** `application/json`

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Path to the codebase to analyze |
| `exclude` | array | No | Patterns to exclude |
| `include` | array | No | Patterns to include |
| `max_depth` | integer | No | Maximum directory depth |
| `extractors` | array | No | Specific extractors to use |
| `output_format` | string | No | Format of results (`json`, `markdown`, `html`) |
| `async` | boolean | No | Whether to run asynchronously (default: true) |

**Example Request:**
```bash
curl -X POST https://your-server/api/v1/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "path": "/path/to/project",
    "exclude": ["node_modules", "*.pyc"],
    "include": ["src/**/*.py", "lib/**/*.js"],
    "max_depth": 5,
    "extractors": ["file-tree", "python-deps", "metrics"],
    "output_format": "json",
    "async": true
  }'
```

**Example Response (202 Accepted):**
```json
{
  "job_id": "abc123",
  "status": "processing",
  "results_url": "/api/v1/jobs/abc123",
  "estimated_time": "30s"
}
```

### Get Available Extractors

Returns information about available extractors that can be used in analysis.

**Endpoint:** `/api/v1/extractors`  
**Method:** GET  
**Authentication:** Required  

**Example Request:**
```bash
curl -H "Authorization: Bearer your-jwt-token" \
  https://your-server/api/v1/extractors
```

**Example Response (200 OK):**
```json
{
  "extractors": [
    {
      "id": "file-tree",
      "name": "File Tree Extractor",
      "description": "Extracts the file structure of the codebase",
      "supported_languages": ["*"],
      "parameters": [
        {
          "name": "max_depth",
          "type": "integer",
          "description": "Maximum directory depth",
          "default": 10
        }
      ]
    },
    {
      "id": "python-deps",
      "name": "Python Dependencies Extractor",
      "description": "Extracts Python import dependencies",
      "supported_languages": ["python"],
      "parameters": []
    }
  ]
}
```

## Extraction Endpoints

### Submit Extraction Job

Extracts specific information from a codebase.

**Endpoint:** `/api/v1/extract`  
**Method:** POST  
**Authentication:** Required  
**Content-Type:** `application/json`

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Path to the codebase to analyze |
| `extractors` | array | Yes | List of extractors to use |
| `exclude` | array | No | Patterns to exclude |
| `include` | array | No | Patterns to include |
| `options` | object | No | Extractor-specific options |
| `output_format` | string | No | Format of results (`json`, `markdown`, `html`) |

**Example Request:**
```bash
curl -X POST https://your-server/api/v1/extract \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "path": "/path/to/project",
    "extractors": ["file-tree", "python-deps"],
    "exclude": ["node_modules", "*.pyc"],
    "include": ["src/**/*.py"],
    "options": {
      "python-deps": {
        "resolve_external": true
      }
    },
    "output_format": "json"
  }'
```

**Example Response (202 Accepted):**
```json
{
  "job_id": "def456",
  "status": "processing",
  "results_url": "/api/v1/jobs/def456",
  "estimated_time": "15s"
}
```

## Visualization Endpoints

### Generate Visualization

Generates visualizations from analysis results.

**Endpoint:** `/api/v1/visualize`  
**Method:** POST  
**Authentication:** Required  
**Content-Type:** `application/json`

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
curl -X POST https://your-server/api/v1/visualize \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "job_id": "abc123",
    "type": "dependency-graph",
    "format": "svg",
    "options": {
      "group_by": "package",
      "include_external": false,
      "color_scheme": "blue",
      "layout": "hierarchical"
    }
  }'
```

**Example Response (202 Accepted):**
```json
{
  "job_id": "ghi789",
  "status": "processing",
  "results_url": "/api/v1/jobs/ghi789",
  "estimated_time": "5s"
}
```

### Get Available Visualization Types

Returns information about available visualization types.

**Endpoint:** `/api/v1/visualizations`  
**Method:** GET  
**Authentication:** Required  

**Example Request:**
```bash
curl -H "Authorization: Bearer your-jwt-token" \
  https://your-server/api/v1/visualizations
```

**Example Response (200 OK):**
```json
{
  "visualization_types": [
    {
      "id": "dependency-graph",
      "name": "Dependency Graph",
      "description": "Graph showing dependencies between modules",
      "supported_formats": ["svg", "png", "pdf"],
      "options": [
        {
          "name": "group_by",
          "type": "string",
          "description": "How to group nodes",
          "allowed_values": ["package", "module", "file"],
          "default": "module"
        }
      ]
    },
    {
      "id": "treemap",
      "name": "Treemap",
      "description": "Hierarchical view of codebase size",
      "supported_formats": ["svg", "png", "pdf"],
      "options": []
    }
  ]
}
```

## Metrics Endpoints

### Calculate Metrics

Calculates metrics for a codebase.

**Endpoint:** `/api/v1/metrics`  
**Method:** POST  
**Authentication:** Required  
**Content-Type:** `application/json`

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Path to the codebase to analyze |
| `metrics` | array | No | Specific metrics to calculate (defaults to all) |
| `exclude` | array | No | Patterns to exclude |
| `include` | array | No | Patterns to include |
| `options` | object | No | Metric-specific options |

**Example Request:**
```bash
curl -X POST https://your-server/api/v1/metrics \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "path": "/path/to/project",
    "metrics": ["loc", "complexity", "dependencies"],
    "exclude": ["node_modules", "*.pyc"],
    "include": ["src/**/*.py"],
    "options": {
      "complexity": {
        "max_threshold": 15
      }
    }
  }'
```

**Example Response (202 Accepted):**
```json
{
  "job_id": "jkl012",
  "status": "processing",
  "results_url": "/api/v1/jobs/jkl012",
  "estimated_time": "10s"
}
```

### Get Available Metrics

Returns information about available metrics that can be calculated.

**Endpoint:** `/api/v1/metrics/types`  
**Method:** GET  
**Authentication:** Required  

**Example Request:**
```bash
curl -H "Authorization: Bearer your-jwt-token" \
  https://your-server/api/v1/metrics/types
```

**Example Response (200 OK):**
```json
{
  "metric_types": [
    {
      "id": "loc",
      "name": "Lines of Code",
      "description": "Counts physical lines of code",
      "supported_languages": ["*"],
      "options": []
    },
    {
      "id": "complexity",
      "name": "Cyclomatic Complexity",
      "description": "Measures code complexity",
      "supported_languages": ["python", "javascript", "java"],
      "options": [
        {
          "name": "max_threshold",
          "type": "integer",
          "description": "Maximum complexity threshold",
          "default": 10
        }
      ]
    }
  ]
}
```

## Summary Endpoints

### Generate Summary

Generates a summary of codebase analysis.

**Endpoint:** `/api/v1/summary`  
**Method:** POST  
**Authentication:** Required  
**Content-Type:** `application/json`

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `job_id` | string | Yes* | ID of a completed analysis job |
| `data` | object | Yes* | Raw analysis data for summarization |
| `format` | string | No | Format of results (`json`, `markdown`, `html`) |
| `detail_level` | string | No | Detail level (`brief`, `standard`, `detailed`) |
| `sections` | array | No | Specific sections to include |

\* Either `job_id` or `data` must be provided

**Example Request:**
```bash
curl -X POST https://your-server/api/v1/summary \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "job_id": "abc123",
    "format": "markdown",
    "detail_level": "standard",
    "sections": ["overview", "dependencies", "complexity"]
  }'
```

**Example Response (202 Accepted):**
```json
{
  "job_id": "mno345",
  "status": "processing",
  "results_url": "/api/v1/jobs/mno345",
  "estimated_time": "5s"
}
```

## Change Detection Endpoints

### Analyze Changes

Analyzes changes between two versions of a codebase.

**Endpoint:** `/api/v1/changes`  
**Method:** POST  
**Authentication:** Required  
**Content-Type:** `application/json`

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Path to the codebase |
| `base_ref` | string | Yes | Base reference (commit/tag) |
| `target_ref` | string | No | Target reference (commit/tag, defaults to current state) |
| `extractors` | array | No | Specific extractors to use |
| `output_format` | string | No | Format of results (`json`, `markdown`, `html`) |

**Example Request:**
```bash
curl -X POST https://your-server/api/v1/changes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "path": "/path/to/project",
    "base_ref": "v1.0.0",
    "target_ref": "main",
    "extractors": ["dependencies", "metrics"],
    "output_format": "json"
  }'
```

**Example Response (202 Accepted):**
```json
{
  "job_id": "pqr678",
  "status": "processing",
  "results_url": "/api/v1/jobs/pqr678",
  "estimated_time": "45s"
}
```

## Job Management Endpoints

### Get Job Status

Returns the status of a specific job.

**Endpoint:** `/api/v1/jobs/{job_id}`  
**Method:** GET  
**Authentication:** Required  

**Example Request:**
```bash
curl -H "Authorization: Bearer your-jwt-token" \
  https://your-server/api/v1/jobs/abc123
```

**Example Response (200 OK):**
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

Returns the result of a completed job.

**Endpoint:** `/api/v1/jobs/{job_id}/result`  
**Method:** GET  
**Authentication:** Required  

**Example Request:**
```bash
curl -H "Authorization: Bearer your-jwt-token" \
  https://your-server/api/v1/jobs/abc123/result
```

The response will contain the result of the job, with a Content-Type appropriate for the result format (JSON, image, etc.).

### List Jobs

Returns a list of jobs for the authenticated user.

**Endpoint:** `/api/v1/jobs`  
**Method:** GET  
**Authentication:** Required  

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by status (`pending`, `processing`, `completed`, `failed`) |
| `type` | string | No | Filter by job type |
| `limit` | integer | No | Maximum number of jobs to return (default: 10) |
| `offset` | integer | No | Pagination offset (default: 0) |

**Example Request:**
```bash
curl -H "Authorization: Bearer your-jwt-token" \
  "https://your-server/api/v1/jobs?status=completed&limit=5"
```

**Example Response (200 OK):**
```json
{
  "jobs": [
    {
      "job_id": "abc123",
      "type": "analysis",
      "status": "completed",
      "created_at": "2023-01-01T12:00:00Z",
      "completed_at": "2023-01-01T12:01:30Z"
    },
    {
      "job_id": "def456",
      "type": "extraction",
      "status": "completed",
      "created_at": "2023-01-01T11:30:00Z",
      "completed_at": "2023-01-01T11:30:45Z"
    }
  ],
  "total": 27,
  "limit": 5,
  "offset": 0
}
```

### Cancel Job

Cancels a running job.

**Endpoint:** `/api/v1/jobs/{job_id}/cancel`  
**Method:** POST  
**Authentication:** Required  

**Example Request:**
```bash
curl -X POST -H "Authorization: Bearer your-jwt-token" \
  https://your-server/api/v1/jobs/abc123/cancel
```

**Example Response (200 OK):**
```json
{
  "job_id": "abc123",
  "status": "cancelled",
  "message": "Job cancelled successfully"
}
```

## Authentication Endpoints

### Obtain JWT Token

Obtains a JWT access token and refresh token.

**Endpoint:** `/api/v1/auth/token`  
**Method:** POST  
**Authentication:** None  
**Content-Type:** `application/json`

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | string | Yes | Username |
| `password` | string | Yes | Password |

**Example Request:**
```bash
curl -X POST https://your-server/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "your-username", "password": "your-password"}'
```

**Example Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Refresh JWT Token

Refreshes an expired JWT access token.

**Endpoint:** `/api/v1/auth/refresh`  
**Method:** POST  
**Authentication:** None  
**Content-Type:** `application/json`

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `refresh_token` | string | Yes | Valid refresh token |

**Example Request:**
```bash
curl -X POST https://your-server/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your-refresh-token"}'
```

**Example Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Revoke Token

Revokes a JWT token.

**Endpoint:** `/api/v1/auth/revoke`  
**Method:** POST  
**Authentication:** Required  
**Content-Type:** `application/json`

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `token` | string | Yes | Token to revoke |
| `token_type_hint` | string | No | Type of token (`access_token` or `refresh_token`) |

**Example Request:**
```bash
curl -X POST https://your-server/api/v1/auth/revoke \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{"token": "token-to-revoke", "token_type_hint": "refresh_token"}'
```

**Example Response (200 OK):**
```json
{
  "message": "Token revoked successfully"
}
```

## API Key Management Endpoints

### Create API Key

Creates a new API key.

**Endpoint:** `/api/v1/auth/keys`  
**Method:** POST  
**Authentication:** Required (with admin permissions)  
**Content-Type:** `application/json`

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Name of the API key |
| `scopes` | array | No | List of permission scopes |
| `expires_at` | string | No | Expiration date (ISO 8601 format) |

**Example Request:**
```bash
curl -X POST https://your-server/api/v1/auth/keys \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "name": "Production API",
    "scopes": ["read", "write"],
    "expires_at": "2024-12-31T23:59:59Z"
  }'
```

**Example Response (201 Created):**
```json
{
  "key_id": "key123",
  "api_key": "ca123456789abcdef",
  "name": "Production API",
  "scopes": ["read", "write"],
  "created_at": "2023-01-01T12:00:00Z",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

**Note**: The `api_key` field is only returned once when the key is created.

### List API Keys

Lists all API keys for the current user.

**Endpoint:** `/api/v1/auth/keys`  
**Method:** GET  
**Authentication:** Required  

**Example Request:**
```bash
curl -H "Authorization: Bearer your-jwt-token" \
  https://your-server/api/v1/auth/keys
```

**Example Response (200 OK):**
```json
{
  "keys": [
    {
      "key_id": "key123",
      "name": "Production API",
      "scopes": ["read", "write"],
      "created_at": "2023-01-01T12:00:00Z",
      "expires_at": "2024-12-31T23:59:59Z"
    },
    {
      "key_id": "key456",
      "name": "Development API",
      "scopes": ["read", "write", "admin"],
      "created_at": "2023-01-01T11:00:00Z",
      "expires_at": null
    }
  ]
}
```

### Revoke API Key

Revokes an API key.

**Endpoint:** `/api/v1/auth/keys/{key_id}`  
**Method:** DELETE  
**Authentication:** Required  

**Example Request:**
```bash
curl -X DELETE -H "Authorization: Bearer your-jwt-token" \
  https://your-server/api/v1/auth/keys/key123
```

**Example Response (200 OK):**
```json
{
  "message": "API key revoked successfully",
  "key_id": "key123"
}
```

## OAuth2 Endpoints

### Register OAuth Client

Registers a new OAuth2 client application.

**Endpoint:** `/api/v1/auth/oauth/clients`  
**Method:** POST  
**Authentication:** Required (with admin permissions)  
**Content-Type:** `application/json`

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Client application name |
| `redirect_uris` | array | Yes | Allowed redirect URIs |
| `allowed_scopes` | array | No | Allowed permission scopes |
| `description` | string | No | Client description |

**Example Request:**
```bash
curl -X POST https://your-server/api/v1/auth/oauth/clients \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "name": "My Integration",
    "redirect_uris": ["https://my-app.com/callback"],
    "allowed_scopes": ["read", "write"],
    "description": "Integration with My Application"
  }'
```

**Example Response (201 Created):**
```json
{
  "client_id": "client123",
  "client_secret": "cs123456789abcdef",
  "name": "My Integration",
  "redirect_uris": ["https://my-app.com/callback"],
  "allowed_scopes": ["read", "write"],
  "created_at": "2023-01-01T12:00:00Z"
}
```

**Note**: The `client_secret` field is only returned once when the client is created.

## Webhooks Endpoints

### Create Webhook

Creates a new webhook for receiving event notifications.

**Endpoint:** `/api/v1/webhooks`  
**Method:** POST  
**Authentication:** Required  
**Content-Type:** `application/json`

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | Webhook URL |
| `events` | array | Yes | Events to subscribe to |
| `name` | string | No | Webhook name |
| `secret` | string | No | Secret for webhook signature |
| `active` | boolean | No | Whether the webhook is active (default: true) |

**Example Request:**
```bash
curl -X POST https://your-server/api/v1/webhooks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "url": "https://my-app.com/webhook",
    "events": ["job.completed", "analysis.completed"],
    "name": "Job Notification",
    "secret": "my-webhook-secret",
    "active": true
  }'
```

**Example Response (201 Created):**
```json
{
  "webhook_id": "wh123",
  "url": "https://my-app.com/webhook",
  "events": ["job.completed", "analysis.completed"],
  "name": "Job Notification",
  "active": true,
  "created_at": "2023-01-01T12:00:00Z"
}
```

### List Webhooks

Lists all webhooks for the current user.

**Endpoint:** `/api/v1/webhooks`  
**Method:** GET  
**Authentication:** Required  

**Example Request:**
```bash
curl -H "Authorization: Bearer your-jwt-token" \
  https://your-server/api/v1/webhooks
```

**Example Response (200 OK):**
```json
{
  "webhooks": [
    {
      "webhook_id": "wh123",
      "url": "https://my-app.com/webhook",
      "events": ["job.completed", "analysis.completed"],
      "name": "Job Notification",
      "active": true,
      "created_at": "2023-01-01T12:00:00Z"
    }
  ]
}
```

### Test Webhook

Sends a test event to a webhook.

**Endpoint:** `/api/v1/webhooks/{webhook_id}/test`  
**Method:** POST  
**Authentication:** Required  

**Example Request:**
```bash
curl -X POST -H "Authorization: Bearer your-jwt-token" \
  https://your-server/api/v1/webhooks/wh123/test
```

**Example Response (200 OK):**
```json
{
  "webhook_id": "wh123",
  "delivered": true,
  "status_code": 200,
  "message": "Test webhook delivered successfully"
}
```

## Error Handling

All endpoints use standard HTTP status codes and a consistent error response format:

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

Common error codes include:

- `INVALID_PARAMETER`: A request parameter is invalid or missing
- `AUTHENTICATION_REQUIRED`: Authentication is required
- `INVALID_CREDENTIALS`: The provided credentials are invalid
- `PERMISSION_DENIED`: The authenticated user lacks required permissions
- `RESOURCE_NOT_FOUND`: The requested resource doesn't exist
- `RATE_LIMIT_EXCEEDED`: The rate limit has been exceeded
- `INTERNAL_ERROR`: An internal server error occurred 