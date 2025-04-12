"""
Configuration settings for the Codex-Arch REST API.
"""

import os
from typing import Dict, Any, Optional

class Config:
    """Base configuration class for the API."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'development-secret-key')
    OUTPUT_DIR = os.environ.get('OUTPUT_DIR', os.path.join(os.getcwd(), 'output'))
    UPLOAD_FOLDER = os.path.join(OUTPUT_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload size
    JWT_EXPIRATION = 3600  # 1 hour
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    CACHE_TYPE = os.environ.get('CACHE_TYPE', "SimpleCache")
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))  # 5 minutes
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_DIR = os.environ.get('CACHE_DIR', os.path.join(os.getcwd(), 'cache'))
    CACHE_THRESHOLD = int(os.environ.get('CACHE_THRESHOLD', 1000))  # Max items in cache
    CACHE_OPTIONS = {
        'CACHE_REDIS_HOST': os.environ.get('REDIS_HOST', 'localhost'),
        'CACHE_REDIS_PORT': int(os.environ.get('REDIS_PORT', 6379)),
        'CACHE_REDIS_DB': int(os.environ.get('REDIS_DB', 0)),
        'CACHE_KEY_PREFIX': 'codex-arch_',
    }
    DISABLE_CACHE_IN_DEBUG = os.environ.get('DISABLE_CACHE_IN_DEBUG', 'false').lower() == 'true'
    API_VERSION = "v1"
    API_TITLE = "Codex-Arch API"


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    

class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True
    CACHE_TYPE = "NullCache"  # Disable caching in testing


class ProductionConfig(Config):
    """Production environment configuration."""
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'https://yourdomain.com')
    # Use Redis in production if available, otherwise FileSystemCache
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'FileSystemCache' if os.environ.get('CACHE_DIR') else 'SimpleCache')
    # Longer timeout in production
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 3600))  # 1 hour
    
    def __init__(self):
        """Initialize production configuration with environment variables."""
        super().__init__()
        # Override SECRET_KEY with environment variable
        if 'SECRET_KEY' in os.environ:
            self.SECRET_KEY = os.environ['SECRET_KEY']


# Configuration dictionary based on environment
config_by_name = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig
}

def get_config() -> Config:
    """Get the current configuration based on environment."""
    env = os.environ.get('API_ENV', 'dev')
    return config_by_name.get(env, DevelopmentConfig) 