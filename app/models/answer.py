"""
Answer Model
Represents a single answer within an assessment.
"""

from app.extensions import db
from app.models.base import BaseModel


class Answer(BaseModel):
    """
    Answer model for storing individual assessment responses.
    """
    
    __tablename__ = 'answers'
    
    # Answer information
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    question_id = db.Column(db.String(10), nullable=False)
    question_text = db.Column(db.Text, nullable=True)  # ALLOW NULL
    answer_text = db.Column(db.String(200), nullable=True)  # ALLOW NULL
    answer_value = db.Column(db.Float, nullable=False)
    score = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(20), nullable=True)
    question_type = db.Column(db.String(20), nullable=True)
    
    def to_dict(self):
        """
        Convert answer instance to dictionary.
        
        Returns:
            dict: Answer data
        """
        data = super().to_dict()
        data.update({
            'question_text': self.question_text,
            'question_id': self.question_id,
            'answer_text': self.answer_text,
            'answer_value': self.answer_value,
            'score': self.score,
            'category': self.category,
            'question_type': self.question_type,
            'assessment_id': self.assessment_id
        })
        return data
    
    def __repr__(self):
        return f'<Answer {self.question_id} - Score: {self.score}>'
