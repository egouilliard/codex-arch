"""
Tests for the API configuration module.
"""

import os
import pytest
from unittest.mock import patch

from codex_arch.api.config import Config, DevelopmentConfig, TestingConfig, ProductionConfig, get_config


class TestAPIConfig:
    """Test cases for the API configuration."""

    def test_default_config(self):
        """Test the default configuration values."""
        config = Config()
        
        # Check default values
        assert config.DEBUG is False
        assert config.TESTING is False
        assert config.SECRET_KEY == 'development-secret-key'
        assert config.CACHE_TYPE == "SimpleCache"
        assert config.API_VERSION == "v1"
        assert config.API_TITLE == "Codex-Arch API"
        
    def test_development_config(self):
        """Test development configuration."""
        config = DevelopmentConfig()
        assert config.DEBUG is True
        
    def test_testing_config(self):
        """Test testing configuration."""
        config = TestingConfig()
        assert config.TESTING is True
        assert config.DEBUG is True
        assert config.CACHE_TYPE == "NullCache"
        
    def test_production_config(self):
        """Test production configuration."""
        # Need to patch os.environ.get to provide SECRET_KEY
        with patch.dict(os.environ, {"SECRET_KEY": "production-secret"}):
            config = ProductionConfig()
            assert config.SECRET_KEY == "production-secret"
            assert config.CACHE_TYPE == "SimpleCache"  # Default when CACHE_DIR not set
            assert config.CACHE_DEFAULT_TIMEOUT == 3600
        
    def test_get_config_default(self):
        """Test the get_config function returns development config by default."""
        # Make sure API_ENV is not set
        with patch.dict(os.environ, {}, clear=True):
            config_class = get_config()
            assert config_class == DevelopmentConfig
    
    def test_get_config_development(self):
        """Test the get_config function with development environment."""
        with patch.dict(os.environ, {"API_ENV": "dev"}):
            config_class = get_config()
            assert config_class == DevelopmentConfig
    
    def test_get_config_testing(self):
        """Test the get_config function with testing environment."""
        with patch.dict(os.environ, {"API_ENV": "test"}):
            config_class = get_config()
            assert config_class == TestingConfig
    
    def test_get_config_production(self):
        """Test the get_config function with production environment."""
        with patch.dict(os.environ, {"API_ENV": "prod"}):
            config_class = get_config()
            assert config_class == ProductionConfig