"""
Logger Setup Module
Configures application logging for development and production.
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(app):
    """
    Setup logging configuration for the Flask application.
    
    Args:
        app: Flask application instance
    """
    # Ensure log directory exists
    log_dir = os.path.dirname(app.config.get('LOG_FILE', 'logs/app.log'))
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Set log level from config
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    
    # Create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # File handler with rotation
    log_file = app.config.get('LOG_FILE')
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)
    
    # Set application logger level
    app.logger.setLevel(log_level)
    
    # Log startup message
    app.logger.info(f'{app.config.get("APP_NAME")} starting up...')
