"""
SkillPlan Model
Represents a personalised skill plan for a student.
"""

from app.extensions import db
from app.models.base import BaseModel


class SkillPlan(BaseModel):
    """
    SkillPlan model for storing student skill roadmaps.
    """
    
    __tablename__ = 'skill_plans'
    
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    personality_type = db.Column(db.String(100), nullable=False)
    skills = db.Column(db.JSON, nullable=False)  # Array of skills with order, resources, milestones
    
    # Properties for camelCase support
    @property
    def studentId(self):
        return self.student_id
    
    @studentId.setter
    def studentId(self, value):
        self.student_id = value
        
    @property
    def personalityType(self):
        return self.personality_type
    
    @personalityType.setter
    def personalityType(self, value):
        self.personality_type = value
        
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'student_id': self.student_id,
            'studentId': self.student_id,
            'personality_type': self.personality_type,
            'personalityType': self.personality_type,
            'skills': self.skills
        })
        return data

    def __repr__(self):
        return f'<SkillPlan {self.personality_type} for Student {self.student_id}>'
