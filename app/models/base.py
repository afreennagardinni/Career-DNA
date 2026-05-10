"""
Base Model Module
Contains the base model class with common functionality.
"""

from datetime import datetime
from app.extensions import db


class BaseModel(db.Model):
    """
    Base model class that provides common fields and methods.
    All other models should inherit from this class.
    """
    
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def save(self):
        """
        Save the model instance to the database.
        
        Returns:
            The saved model instance
        """
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """
        Delete the model instance from the database.
        
        Returns:
            True if successful
        """
        db.session.delete(self)
        db.session.commit()
        return True
    
    def to_dict(self):
        """
        Convert the model instance to a dictionary.
        
        Returns:
            Dictionary representation of the model
        """
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'
