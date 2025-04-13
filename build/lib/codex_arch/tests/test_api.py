"""
Tests for the API module.
"""

import os
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import flask
from flask import Flask, request

from codex_arch.api.app import create_app
from codex_arch.api.config import Config


class TestAPIConfig:
    """Test cases for the API configuration."""

    def test_default_config(self):
        """Test the default configuration values."""
        config = Config()
        
        # Check default values
        assert config.PORT == 5000
        assert config.DEBUG is False
        assert config.TESTING is False
        assert config.JWT_SECRET_KEY is not None
        assert config.JWT_ACCESS_TOKEN_EXPIRES is not None
        assert config.CACHE_TYPE == "SimpleCache"
        
    def test_from_env_vars(self, monkeypatch):
        """Test loading configuration from environment variables."""
        # Set environment variables
        monkeypatch.setenv("CODEX_ARCH_PORT", "8080")
        monkeypatch.setenv("CODEX_ARCH_DEBUG", "true")
        monkeypatch.setenv("CODEX_ARCH_JWT_SECRET", "test_secret")
        
        # Create config object
        config = Config()
        
        # Verify environment variables were applied
        assert config.PORT == 8080
        assert config.DEBUG is True
        assert config.JWT_SECRET_KEY == "test_secret"
        
    def test_from_file(self, temp_dir):
        """Test loading configuration from a file."""
        # Create a config file
        config_file = temp_dir / "test_config.json"
        config_data = {
            "PORT": 9000,
            "DEBUG": True,
            "JWT_SECRET_KEY": "file_secret"
        }
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        # Load config from file
        config = Config()
        config.from_file(str(config_file))
        
        # Verify file values were applied
        assert config.PORT == 9000
        assert config.DEBUG is True
        assert config.JWT_SECRET_KEY == "file_secret"


class TestAPIApp:
    """Test cases for the Flask application."""

    def test_create_app(self):
        """Test creating the Flask application."""
        app = create_app()
        
        # Verify app was created
        assert app is not None
        assert isinstance(app, Flask)
        
        # Check basic configuration
        assert app.config["TESTING"] is False
        assert "JWT_SECRET_KEY" in app.config
        
    def test_create_app_testing_mode(self):
        """Test creating the app in testing mode."""
        app = create_app(testing=True)
        
        # Verify testing configuration
        assert app.config["TESTING"] is True
        assert app.config["DEBUG"] is True
        
    @patch('flask.Flask.run')
    def test_app_run(self, mock_run):
        """Test running the Flask application."""
        app = create_app()
        app.run(host="0.0.0.0", port=5000)
        
        # Verify run was called with correct parameters
        mock_run.assert_called_once_with(host="0.0.0.0", port=5000)

    def test_routes_registered(self):
        """Test that all expected routes are registered."""
        app = create_app()
        
        # Get all registered routes
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        
        # Check for expected routes
        assert "/" in routes  # Root/index route
        assert "/api/status" in routes  # Status route
        assert "/api/auth/login" in routes  # Auth routes
        
        # Check for API documentation routes
        assert "/api/docs" in routes or "/api/swagger" in routes

    def test_cors_config(self):
        """Test CORS configuration."""
        app = create_app()
        
        # Check that CORS was initialized
        # This is a basic check - full CORS testing would require running the server
        assert app.config.get("CORS_HEADERS") is not None


class TestAPIEndpoints:
    """Test cases for API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client for the Flask application."""
        app = create_app(testing=True)
        with app.test_client() as client:
            yield client

    def test_status_endpoint(self, client):
        """Test the status endpoint."""
        response = client.get("/api/status")
        data = json.loads(response.data)
        
        # Verify response
        assert response.status_code == 200
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "version" in data

    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        
        # Verify response
        assert response.status_code == 200
        assert b"ok" in response.data.lower()

    def test_unauthorized_access(self, client):
        """Test accessing protected endpoints without authentication."""
        # Try to access a protected endpoint
        response = client.get("/api/analysis")
        
        # Verify authentication failure
        assert response.status_code in [401, 403]  # Unauthorized or Forbidden

    @patch("codex_arch.api.auth.jwt.decode_token")
    def test_authorized_access(self, mock_decode, client):
        """Test accessing protected endpoints with authentication."""
        # Mock JWT token validation
        mock_decode.return_value = {"sub": "test_user", "permissions": ["read"]}
        
        # Access with mocked Authorization header
        response = client.get(
            "/api/analysis",
            headers={"Authorization": "Bearer fake_token"}
        )
        
        # This test may fail if the endpoint returns errors for other reasons
        # In a real test, we would mock any backend services the endpoint calls
        assert response.status_code != 401  # Should not be unauthorized

    def test_docs_endpoint(self, client):
        """Test the API documentation endpoint."""
        response = client.get("/api/docs")
        
        # Verify documentation is served
        assert response.status_code == 200
        assert b"swagger" in response.data.lower() or b"openapi" in response.data.lower() 