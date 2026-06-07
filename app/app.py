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
from threading import Thread
import time
from app.models.user import User
from app.services.drift_service import PersonalityDriftService


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
            from app.utils.seed_db import seed_database
            seed_database()
    
    # Background scheduler for weekly personality drift calculations
    def start_drift_scheduler(app):
        interval = app.config.get('DRIFT_CHECK_INTERVAL_SECONDS', 7 * 24 * 3600)

        def worker():
            # Simple daemon loop that runs drift checks periodically
            while True:
                try:
                    with app.app_context():
                        # Fetch active users and run analysis
                        users = User.query.filter_by(is_active=True).all()
                        for u in users:
                            try:
                                PersonalityDriftService.calculate_drift(u.id)
                            except Exception:
                                app.logger.exception('Error calculating drift for user %s', u.id)
                except Exception:
                    app.logger.exception('Drift scheduler encountered an error')
                time.sleep(interval)

        thread = Thread(target=worker, daemon=True)
        thread.start()

    # Only start scheduler when explicitly enabled in config
    if app.config.get('ENABLE_DRIFT_SCHEDULER', False):
        start_drift_scheduler(app)

    return app


def register_blueprints(app):
    """
    Register all Flask blueprints.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(auth, url_prefix='/auth')
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
    from flask import render_template
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', error='Page Not Found',
                               message='The requested resource was not found.'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server error: {error}')
        return render_template('error.html', error='Internal Server Error',
                               message='An unexpected error occurred. Please try again.'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('error.html', error='Access Forbidden',
                               message='You do not have permission to access this resource.'), 403


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
