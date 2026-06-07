"""
Notification Model
Represents a notification in the system.
"""

from datetime import datetime
from app.extensions import db
from app.models.base import BaseModel


class Notification(BaseModel):
    """
    Notification model for user alerts.
    """
    
    __tablename__ = 'notifications'
    
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)  # enum values: 'PersonalisedVideoAlert', 'MentorMessage', 'SkillPlanUpdate', 'WeeklyProgressNudge'
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    link_to = db.Column(db.String(255))
    
    # Relationships
    student = db.relationship('User', backref=db.backref('notifications', lazy='dynamic', cascade='all, delete-orphan'))
    
    # Properties for camelCase support
    @property
    def studentId(self):
        return self.student_id
    
    @studentId.setter
    def studentId(self, value):
        self.student_id = value
        
    @property
    def isRead(self):
        return self.is_read
    
    @isRead.setter
    def isRead(self, value):
        self.is_read = value
        
    @property
    def linkTo(self):
        return self.link_to
    
    @linkTo.setter
    def linkTo(self, value):
        self.link_to = value
        
    @property
    def createdAt(self):
        return self.created_at
    
    @createdAt.setter
    def createdAt(self, value):
        self.created_at = value
        
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'student_id': self.student_id,
            'studentId': self.student_id,
            'type': self.type,
            'message': self.message,
            'is_read': self.is_read,
            'isRead': self.is_read,
            'link_to': self.link_to,
            'linkTo': self.link_to,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        })
        return data

    def __repr__(self):
        return f'<Notification {self.type} for Student {self.student_id} (read={self.is_read})>'
