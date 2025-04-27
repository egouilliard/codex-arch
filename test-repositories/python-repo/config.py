import os

class Config:
    """
    Base configuration class
    
    Attributes:
        SECRET_KEY (str): Secret key for the app
        SQLALCHEMY_DATABASE_URI (str): SQLite database URI
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Disable modification tracking
    """
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///instance/site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    
    # Pagination
    POSTS_PER_PAGE = 10


class DevelopmentConfig(Config):
    """
    Development configuration
    
    Attributes:
        DEBUG (bool): Enable debug mode
    """
    DEBUG = True
    
    # Development-specific settings
    SQLALCHEMY_ECHO = True  # Log SQL statements
    TEMPLATES_AUTO_RELOAD = True  # Auto-reload templates


class TestingConfig(Config):
    """
    Testing configuration
    
    Attributes:
        TESTING (bool): Enable testing mode
        SQLALCHEMY_DATABASE_URI (str): In-memory SQLite database
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF protection in tests
    WTF_CSRF_ENABLED = False
    
    # Faster bcrypt for testing
    BCRYPT_LOG_ROUNDS = 4


class ProductionConfig(Config):
    """
    Production configuration
    
    Attributes:
        DEBUG (bool): Disable debug mode
    """
    DEBUG = False
    
    # Production-specific settings
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_RECYCLE = 280
    
    # Security settings
    PREFERRED_URL_SCHEME = 'https'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 