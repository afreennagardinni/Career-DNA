"""
Extensions Module
Centralizes all Flask extensions for easy initialization.
This allows extensions to be initialized without the app context.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def init_extensions(app):
    """
    Initialize all extensions with the Flask app.
    
    Args:
        app: Flask application instance
    """
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configure LoginManager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login."""
        from app.models.user import User
        return User.query.get(int(user_id))
