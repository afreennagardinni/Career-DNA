"""
DailyActivity Model
Tracks user daily activity for gamification.
"""
from datetime import datetime, date
from app.extensions import db
from app.models.base import BaseModel

class DailyActivity(BaseModel):
    """
    DailyActivity model for tracking streak and daily tasks.
    """
    __tablename__ = 'daily_activities'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    challenge_completed = db.Column(db.Boolean, default=False)
    tip_viewed = db.Column(db.Boolean, default=False)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('daily_activities', lazy='dynamic'))
