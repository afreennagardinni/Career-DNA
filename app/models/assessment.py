"""
Assessment Model
Represents a career assessment taken by a user.
"""

from app.extensions import db
from app.models.base import BaseModel


class Assessment(BaseModel):
    """
    Assessment model for tracking user career assessments.
    """
    
    __tablename__ = 'assessments'
    
    # Assessment information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    assessment_type = db.Column(db.String(50), nullable=False)  # e.g., 'personality', 'skills', 'interests'
    status = db.Column(db.String(20), default='in_progress', nullable=False)  # 'in_progress', 'completed', 'abandoned'
    completed_at = db.Column(db.DateTime)
    
    # Scoring
    total_score = db.Column(db.Float)
    max_score = db.Column(db.Float)
    riasec_scores = db.Column(db.Text)
    big5_scores = db.Column(db.Text)
    dna_type = db.Column(db.String(100))
    top_career = db.Column(db.String(100))
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    answers = db.relationship('Answer', backref='assessment', lazy='dynamic', cascade='all, delete-orphan')
    
    def calculate_score(self):
        """
        Calculate the total score from all answers.
        
        Returns:
            float: Total score
        """
        total = sum(answer.score for answer in self.answers if answer.score is not None)
        self.total_score = total
        return total
    
    def mark_completed(self):
        """
        Mark the assessment as completed.
        """
        from datetime import datetime
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        self.calculate_score()
        self.save()
    
    def to_dict(self):
        """
        Convert assessment instance to dictionary.
        
        Returns:
            dict: Assessment data
        """
        data = super().to_dict()
        data.update({
            'title': self.title,
            'description': self.description,
            'assessment_type': self.assessment_type,
            'status': self.status,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_score': self.total_score,
            'max_score': self.max_score,
            'user_id': self.user_id,
            'answer_count': self.answers.count()
        })
        return data
    
    def __repr__(self):
        return f'<Assessment {self.title} - {self.status}>'
