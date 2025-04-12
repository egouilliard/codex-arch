# Authentication

This document outlines the authentication methods supported by the Codex-Arch API, providing options to secure your API interactions based on your security requirements and use cases.

## Authentication Methods Overview

Codex-Arch supports multiple authentication methods to accommodate different security requirements and integration scenarios:

| Method | Use Case | Security Level | Complexity |
|--------|----------|---------------|------------|
| API Keys | Server-to-server, scripts, CLI | Medium | Low |
| JWT Tokens | Web applications, temporary access | High | Medium |
| OAuth 2.0 | User authentication, third-party apps | High | High |

## API Key Authentication

API keys provide a simple way to authenticate with the Codex-Arch API. They are best suited for server-to-server communication, scripts, and CLI tools.

### Creating an API Key

1. Navigate to the Codex-Arch dashboard
2. Go to **Settings** → **API Keys**
3. Click **Create New API Key**
4. Name your key and select appropriate permissions
5. Copy and securely store your new API key

> **Important**: API keys are only displayed once at creation time. If you lose your key, you'll need to generate a new one.

### Using API Key Authentication

Include your API key in the `Authorization` header of your requests:

```bash
curl -X GET "https://your-server/api/v1/status" \
  -H "Authorization: ApiKey YOUR_API_KEY"
```

For language-specific examples:

#### Python
```python
import requests

headers = {
    "Authorization": "ApiKey YOUR_API_KEY"
}

response = requests.get("https://your-server/api/v1/status", headers=headers)
print(response.json())
```

#### JavaScript
```javascript
fetch('https://your-server/api/v1/status', {
  headers: {
    'Authorization': 'ApiKey YOUR_API_KEY'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

### API Key Best Practices

- Never expose API keys in client-side code
- Use environment variables to store keys in your applications
- Create separate keys for different applications or services
- Apply the principle of least privilege when assigning permissions
- Regularly rotate keys, especially for production environments
- Revoke unused or compromised keys immediately

## JWT Authentication

JSON Web Tokens (JWT) provide a secure way to authenticate and maintain sessions with the Codex-Arch API. JWTs are ideal for web applications where user sessions need to be maintained.

### Obtaining a JWT

JWTs are typically obtained through a login process:

```bash
curl -X POST "https://your-server/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

The response will include your JWT token:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2023-01-01T12:00:00Z"
}
```

### Using JWT Authentication

Include the JWT in the `Authorization` header of your requests:

```bash
curl -X GET "https://your-server/api/v1/analyze" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

For language-specific examples:

#### Python
```python
import requests

headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN"
}

response = requests.get("https://your-server/api/v1/analyze", headers=headers)
print(response.json())
```

#### JavaScript
```javascript
fetch('https://your-server/api/v1/analyze', {
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

### JWT Refresh

JWTs have an expiration time. To maintain a session, you'll need to refresh the token before it expires:

```bash
curl -X POST "https://your-server/api/v1/auth/refresh" \
  -H "Authorization: Bearer YOUR_CURRENT_JWT_TOKEN"
```

The response will include a new token:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2023-01-01T13:00:00Z"
}
```

### JWT Best Practices

- Store JWTs securely (e.g., in HTTP-only cookies)
- Implement proper token refresh mechanisms
- Set appropriate expiration times (short-lived tokens are more secure)
- Include only necessary claims in payload to minimize token size
- Validate tokens on each request
- Implement token revocation mechanisms for logout or security breaches

## OAuth 2.0 Authentication

OAuth 2.0 provides a robust framework for authorization, allowing third-party applications to access resources on behalf of users without exposing their credentials.

### OAuth 2.0 Flow Types Supported

Codex-Arch supports the following OAuth 2.0 flows:

1. **Authorization Code Flow**: For web applications with a server component
2. **Implicit Flow**: For browser-based applications
3. **Client Credentials Flow**: For server-to-server communication
4. **Resource Owner Password Credentials**: For trusted first-party applications

### OAuth 2.0 Configuration

To use OAuth 2.0, you first need to register your application:

1. Navigate to the Codex-Arch dashboard
2. Go to **Settings** → **OAuth Applications**
3. Click **Register New Application**
4. Provide the application name, redirect URI, and select appropriate scopes
5. Note your Client ID and Client Secret

### Authorization Code Flow Example

#### Step 1: Redirect to authorization endpoint

Redirect the user to the authorization endpoint:

```
https://your-server/api/v1/oauth/authorize?
  response_type=code&
  client_id=YOUR_CLIENT_ID&
  redirect_uri=https://your-app.com/callback&
  scope=read_analysis write_analysis&
  state=random_state_string
```

#### Step 2: Exchange authorization code for access token

After the user authorizes your application, they'll be redirected to your callback URL with an authorization code. Exchange this code for an access token:

```bash
curl -X POST "https://your-server/api/v1/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&
      code=AUTHORIZATION_CODE&
      redirect_uri=https://your-app.com/callback&
      client_id=YOUR_CLIENT_ID&
      client_secret=YOUR_CLIENT_SECRET"
```

The response will include your access token and refresh token:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "def50200...",
  "scope": "read_analysis write_analysis"
}
```

#### Step 3: Use the access token

Include the access token in the `Authorization` header:

```bash
curl -X GET "https://your-server/api/v1/analyze" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Step 4: Refresh the access token

When the access token expires, use the refresh token to obtain a new one:

```bash
curl -X POST "https://your-server/api/v1/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token&
      refresh_token=YOUR_REFRESH_TOKEN&
      client_id=YOUR_CLIENT_ID&
      client_secret=YOUR_CLIENT_SECRET"
```

### OAuth 2.0 Scope Reference

Scopes define the specific permissions your application is requesting:

| Scope | Description |
|-------|-------------|
| `read_analysis` | Read access to analysis results |
| `write_analysis` | Permission to initiate new analyses |
| `read_visualization` | Access to visualization endpoints |
| `admin` | Administrative actions (user management, etc.) |
| `webhooks` | Manage webhook configurations |
| `metrics` | Access to metrics endpoints |

### OAuth 2.0 Best Practices

- Use HTTPS for all OAuth 2.0 endpoints
- Implement PKCE (Proof Key for Code Exchange) for public clients
- Validate redirect URIs strictly
- Use state parameter to prevent CSRF attacks
- Request only the scopes you need
- Store tokens securely
- Implement proper error handling for OAuth flows
- Regularly audit applications with access

## Authentication for Specific Scenarios

### CLI Authentication

For command-line tools, we recommend either:

1. API Key authentication:
   ```bash
   # Set the API key as an environment variable
   export CODEX_ARCH_API_KEY="your-api-key"
   
   # Use it in your CLI commands
   codex-arch analyze --path ./my-project
   ```

2. Device authorization flow for user authentication:
   ```bash
   # Initiate device authentication
   codex-arch login
   
   # The CLI will display a code and URL for the user to visit
   # After authorization, the CLI will store the token locally
   ```

### CI/CD Pipeline Authentication

For CI/CD environments, use API Keys with limited permissions:

```yaml
# GitHub Actions example
steps:
  - name: Run Codex-Arch Analysis
    run: codex-arch analyze --path .
    env:
      CODEX_ARCH_API_KEY: ${{ secrets.CODEX_ARCH_API_KEY }}
```

Best practices for CI/CD authentication:
- Store API keys as protected CI/CD variables/secrets
- Create dedicated CI/CD API keys with minimal permissions
- Rotate keys regularly
- Consider using short-lived tokens for heightened security

### Service-to-Service Authentication

For service-to-service communication, use either:

1. API Key authentication
2. OAuth 2.0 Client Credentials flow:
   ```bash
   # Get an access token
   curl -X POST "https://your-server/api/v1/oauth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=client_credentials&
         client_id=YOUR_CLIENT_ID&
         client_secret=YOUR_CLIENT_SECRET&
         scope=read_analysis write_analysis"
   ```

## Security Considerations

### Token Storage

- **Browser**: For web applications, store access tokens in memory or HTTP-only cookies
- **Mobile**: Use secure storage options like Keychain (iOS) or EncryptedSharedPreferences (Android)
- **Desktop**: Use system keychain or encrypted storage
- **Server**: Use environment variables or secure credential stores

### Transport Security

All API requests must use HTTPS. Unencrypted HTTP requests will be rejected.

### Detecting and Handling Security Breaches

If you suspect a security breach:

1. Revoke the affected API keys or tokens immediately
2. Generate new credentials
3. Contact support@codex-arch.com to report the incident
4. Review access logs for suspicious activity

## Troubleshooting

### Common Authentication Errors

| Error | Description | Solution |
|-------|-------------|----------|
| `401 Unauthorized` | Invalid or missing credentials | Check that you're providing the correct credentials and using the proper header format |
| `403 Forbidden` | Insufficient permissions | Verify that your API key or token has the necessary permissions |
| `400 Bad Request` during OAuth | Invalid parameters | Check all required OAuth parameters and their format |
| `invalid_grant` | Invalid or expired authorization code/refresh token | Request a new authorization code or use a valid refresh token |
| `invalid_client` | Client authentication failed | Verify your client ID and secret |

### Debugging Authentication Issues

1. Verify the authentication header format:
   - API Key: `Authorization: ApiKey YOUR_API_KEY`
   - JWT/OAuth: `Authorization: Bearer YOUR_TOKEN`

2. Check token expiration:
   - For JWTs, you can decode the token at [jwt.io](https://jwt.io/) to check the expiration
   - For OAuth tokens, check the `expires_in` value from the token response

3. Enable debug logging in your application to see detailed request information

4. Test authentication with a simple endpoint:
   ```bash
   curl -v -X GET "https://your-server/api/v1/status" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

## Rate Limiting and Throttling

Authentication affects rate limits for the Codex-Arch API:

- Unauthenticated requests: 10 requests per minute
- API Key authentication: 60 requests per minute
- JWT/OAuth authentication: 120 requests per minute

Rate limit status is included in response headers:
- `X-RateLimit-Limit`: Total requests allowed in the current period
- `X-RateLimit-Remaining`: Requests remaining in the current period
- `X-RateLimit-Reset`: Time when the rate limit will reset (Unix timestamp)

When rate limits are exceeded, you'll receive a `429 Too Many Requests` response.

## Next Steps

- Review the [API Endpoints Reference](endpoints.md) for detailed API capabilities
- Explore [External Integrations](external-integrations.md) for integration options
- Check our [SDKs](../sdk/overview.md) for language-specific authentication helpers
- Join our community forums for authentication questions and tips 