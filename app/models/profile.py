"""
Profile Model
Represents a user's career profile and DNA.
"""

from app.extensions import db
from app.models.base import BaseModel


class Profile(BaseModel):
    """
    Profile model for storing user career DNA and profile information.
    """
    
    __tablename__ = 'profiles'
    
    # Professional information
    job_title = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    years_of_experience = db.Column(db.Integer)
    education_level = db.Column(db.String(50))
    
    # Career DNA traits (JSON field for flexibility)
    # Will store: personality traits, skills, interests, values, work style
    career_dna = db.Column(db.JSON)  # Example: {"traits": {"leadership": 0.8, "creativity": 0.9}}
    
    # Career preferences
    preferred_work_environment = db.Column(db.String(100))
    work_style_preference = db.Column(db.String(50))  # e.g., 'remote', 'hybrid', 'onsite'
    career_goals = db.Column(db.Text)
    
    # Profile completion status
    completion_percentage = db.Column(db.Integer, default=0)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    def update_career_dna(self, dna_data):
        """
        Update the career DNA with new data.
        
        Args:
            dna_data (dict): New DNA data to merge
        """
        if self.career_dna is None:
            self.career_dna = {}
        self.career_dna.update(dna_data)
        self.save()
    
    def calculate_completion(self):
        """
        Calculate profile completion percentage based on filled fields.
        
        Returns:
            int: Completion percentage (0-100)
        """
        fields = [
            self.job_title, self.industry, self.years_of_experience,
            self.education_level, self.preferred_work_environment,
            self.work_style_preference, self.career_goals, self.career_dna
        ]
        filled = sum(1 for field in fields if field is not None)
        self.completion_percentage = int((filled / len(fields)) * 100)
        self.save()
        return self.completion_percentage
    
    def to_dict(self):
        """
        Convert profile instance to dictionary.
        
        Returns:
            dict: Profile data
        """
        data = super().to_dict()
        data.update({
            'job_title': self.job_title,
            'industry': self.industry,
            'years_of_experience': self.years_of_experience,
            'education_level': self.education_level,
            'career_dna': self.career_dna,
            'preferred_work_environment': self.preferred_work_environment,
            'work_style_preference': self.work_style_preference,
            'career_goals': self.career_goals,
            'completion_percentage': self.completion_percentage,
            'user_id': self.user_id
        })
        return data
    
    def __repr__(self):
        return f'<Profile for User {self.user_id} - {self.completion_percentage}% complete>'
