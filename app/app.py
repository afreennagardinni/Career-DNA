"""
Flask Application Factory
Creates and configures the Flask application using the factory pattern.
"""

import os
from flask import Flask
from config import get_config
from app.extensions import init_extensions
from app.utils.logger import setup_logger
from app.routes import auth, main_bp, advanced_bp
from app.routes.results import results_bp


def create_app(config_class=None):
    """
    Application factory function.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Configured Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_class or 'development')
    app.config.from_object(config)
    
    # Initialize extensions
    init_extensions(app)
    
    # Setup logging
    setup_logger(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register context processors
    register_context_processors(app)
    
    # Add CORS headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # Create database tables (for development only)
    with app.app_context():
        if app.config['DEBUG']:
            from app.extensions import db
            db.create_all()
    
    return app


def register_blueprints(app):
    """
    Register all Flask blueprints.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(auth)
    app.register_blueprint(main_bp)
    app.register_blueprint(advanced_bp, url_prefix='/advanced')
    from app.routes.assessment import assessment_bp
    app.register_blueprint(assessment_bp, url_prefix='/assessment')
    app.register_blueprint(results_bp)


def register_error_handlers(app):
    """
    Register custom error handlers.
    
    Args:
        app: Flask application instance
    """
    from flask import jsonify
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'The requested resource was not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server error: {error}')
        return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden', 'message': 'You do not have permission to access this resource'}), 403


def register_context_processors(app):
    """
    Register template context processors.
    
    Args:
        app: Flask application instance
    """
    @app.context_processor
    def inject_config():
        """Inject configuration variables into templates."""
        return {
            'app_name': app.config.get('APP_NAME'),
            'app_version': app.config.get('APP_VERSION')
        }
