# Codex-Arch API

The Codex-Arch API provides REST endpoints for accessing code analysis functionality and visualizations.

## Getting Started

### API Base URL

The API is accessible at:

```
https://api.codex-arch.example.com/api/v1
```

For local development, use:

```
http://localhost:5000/api/v1
```

### Authentication

Most API endpoints require JWT authentication. Obtain a token by calling the authentication endpoint:

```bash
curl -X POST http://localhost:5000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

Include the token in subsequent requests:

```bash
curl -X GET http://localhost:5000/api/v1/info/status \
  -H "Authorization: Bearer your_token_here"
```

## API Documentation

Interactive API documentation is available at:

```
http://localhost:5000/api/v1/docs
```

The documentation is built using Swagger/OpenAPI and provides a full reference of all available endpoints, parameters, and response formats.

## Core Endpoints

### Authentication

- `POST /api/v1/auth/token` - Get authentication token
- `POST /api/v1/auth/register` - Register a new user
- `GET /api/v1/auth/verify` - Verify authentication token

### Analysis

- `POST /api/v1/analysis/repo` - Start a new analysis
- `GET /api/v1/analysis/{analysis_id}` - Get analysis status
- `GET /api/v1/analysis/{analysis_id}/results` - Get analysis results

### Artifacts

- `GET /api/v1/artifacts/{analysis_id}/dependency-graph` - Get dependency graph
- `GET /api/v1/artifacts/{analysis_id}/metrics` - Get code metrics
- `GET /api/v1/artifacts/{analysis_id}/summary` - Get code summary

### Info

- `GET /api/v1/info/status` - Get API status
- `GET /api/v1/info/version` - Get API version

## Error Handling

The API uses standard HTTP status codes:

- `200 OK` - Request succeeded
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid authentication
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side error

Error responses include a JSON object with an `error` field containing a description of the error.

## Rate Limiting

API requests are subject to rate limiting. Current limits are:

- 100 requests per minute per authenticated user
- 10 requests per minute for unauthenticated requests

Rate limit headers are included in API responses:

- `X-RateLimit-Limit` - Total requests allowed per time window
- `X-RateLimit-Remaining` - Requests remaining in the current time window
- `X-RateLimit-Reset` - Time (in seconds) until the rate limit resets

## CORS Support

The API supports Cross-Origin Resource Sharing (CORS), allowing browser applications to make requests from different domains.

## Caching

Responses include appropriate cache headers. Clients should respect these headers to minimize unnecessary requests.

## Client Libraries

Official client libraries are available for:

- Python: `pip install codex-arch-client`
- JavaScript: `npm install codex-arch-client`

## License

The Codex-Arch API is available under the MIT license. 