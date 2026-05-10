"""
User Model
Represents a user in the Career DNA platform.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models.base import BaseModel


class User(BaseModel):
    """
    User model for authentication and user management.
    """
    
    __tablename__ = 'users'
    
    # Basic user information
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # User profile information
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Gamification
    xp = db.Column(db.Integer, default=0)
    streak_count = db.Column(db.Integer, default=0)
    
    # Relationships
    assessments = db.relationship('Assessment', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """
        Hash and set the user's password.
        
        Args:
            password (str): Plain text password
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verify the user's password.
        
        Args:
            password (str): Plain text password to verify
        
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """
        Get the user's full name.
        
        Returns:
            str: Full name or username if name not set
        """
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.username
    
    # Flask-Login required methods and properties
    def get_id(self):
        """
        Get the user ID for Flask-Login.
        
        Returns:
            str: User ID as string
        """
        return str(self.id)
    
    @property
    def is_authenticated(self):
        """
        Check if user is authenticated.
        
        Returns:
            bool: Always True for authenticated users
        """
        return True
    
    @property
    def is_anonymous(self):
        """
        Check if user is anonymous.
        
        Returns:
            bool: Always False for authenticated users
        """
        return False
    
    def to_dict(self):
        """
        Convert user instance to dictionary.
        
        Returns:
            dict: User data without sensitive information
        """
        data = super().to_dict()
        data.update({
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin
        })
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'
