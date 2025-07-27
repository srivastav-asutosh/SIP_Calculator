
"""
Configuration settings for SIP Calculator Dashboard
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///sip_calculator.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API settings
    API_RATE_LIMIT = "1000 per hour"
    CORS_ORIGINS = ["*"]  # Configure for production

    # SIP Calculator specific settings
    MIN_INVESTMENT = 500
    MAX_INVESTMENT = 100000
    MIN_RETURN_RATE = 1.0
    MAX_RETURN_RATE = 25.0
    MIN_TIME_PERIOD = 1
    MAX_TIME_PERIOD = 50

    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'

    # Cache settings
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

    # Production-specific settings
    CORS_ORIGINS = ["https://yourdomain.com"]  # Update with actual domain
    SSL_REQUIRED = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
