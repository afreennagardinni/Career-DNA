"""
Routes Package
Contains all Flask route blueprints for the application.
"""

from .auth_routes import auth
from .main import main_bp
from .advanced import advanced_bp

__all__ = ['auth', 'main_bp', 'advanced_bp']
