"""
Authentication Service
Handles authentication-related business logic.
"""

from app.extensions import db
from app.models.user import User
from app.models.profile import Profile


class AuthService:
    """
    Service class for authentication operations.
    """
    
    @staticmethod
    def create_user(email, username, password, first_name=None, last_name=None):
        """
        Create a new user with profile.
        
        Args:
            email (str): User email
            username (str): Username
            password (str): Plain text password
            first_name (str, optional): First name
            last_name (str, optional): Last name
        
        Returns:
            User: Created user instance
        
        Raises:
            ValueError: If user already exists
        """
        # Check if user exists
        if User.query.filter_by(email=email).first():
            raise ValueError('Email already registered')
        
        if User.query.filter_by(username=username).first():
            raise ValueError('Username already taken')
        
        # Create user
        user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save()
        
        # Create profile
        profile = Profile(user_id=user.id)
        profile.save()
        
        return user
    
    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate a user with email and password.
        
        Args:
            email (str): User email
            password (str): Plain text password
        
        Returns:
            User: User instance if authentication successful
            None: If authentication fails
        """
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.is_active:
            return user
        
        return None
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Get user by ID.
        
        Args:
            user_id (int): User ID
        
        Returns:
            User: User instance or None
        """
        return User.query.get(user_id)
