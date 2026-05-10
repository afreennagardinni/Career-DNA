"""
Configuration Module
Handles environment-based configuration for the application.
Supports development, testing, and production environments.
"""

import os
from datetime import timedelta


class Config:
    """
    Base configuration class.
    Contains common settings shared across all environments.
    """
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Secret key for session management and CSRF protection
    # In production, this should be set via environment variable
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'career_dna.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'app.log')
    
    # Application settings
    APP_NAME = 'Career DNA Agentic AI Platform'
    APP_VERSION = '1.0.0'
    
    # Pagination
    ITEMS_PER_PAGE = 20


class DevelopmentConfig(Config):
    """
    Development environment configuration.
    Enables debug mode and detailed error messages.
    """
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """
    Testing environment configuration.
    Uses in-memory database for faster tests.
    """
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """
    Production environment configuration.
    Disables debug mode and enables security features.
    """
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    
    # In production, ensure SECRET_KEY is set via environment variable
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.INFO)
        app.logger.addHandler(syslog_handler)


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env_name=None):
    """
    Get configuration class based on environment name.
    
    Args:
        env_name (str): Environment name (development, testing, production)
    
    Returns:
        Config class for the specified environment
    """
    if env_name is None:
        env_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(env_name, config['default'])
