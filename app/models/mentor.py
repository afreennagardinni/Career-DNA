"""
Mentor Model
Represents a mentor in the Career DNA platform.
"""

from app.extensions import db
from app.models.base import BaseModel


class Mentor(BaseModel):
    """
    Mentor model for storing mentor profiles.
    """
    
    __tablename__ = 'mentors'
    
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(150))
    college = db.Column(db.String(150))
    dna_match = db.Column(db.String(150))
    photo_initial = db.Column(db.String(10))
    color = db.Column(db.String(50), default='#0d9488')
    story = db.Column(db.Text)
    quote = db.Column(db.Text)
    advice = db.Column(db.JSON)  # Array of strings
    his_path = db.Column(db.Text)
    
    # Required for personalised content engine
    personality_type = db.Column(db.String(100), nullable=False, index=True)
    is_available = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    # Properties for camelCase support
    @property
    def personalityType(self):
        return self.personality_type
    
    @personalityType.setter
    def personalityType(self, value):
        self.personality_type = value
        
    @property
    def isAvailable(self):
        return self.is_available
    
    @isAvailable.setter
    def isAvailable(self, value):
        self.is_available = value
        
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'name': self.name,
            'role': self.role,
            'college': self.college,
            'dna_match': self.dna_match,
            'photo_initial': self.photo_initial,
            'color': self.color,
            'story': self.story,
            'quote': self.quote,
            'advice': self.advice,
            'his_path': self.his_path,
            'personality_type': self.personality_type,
            'personalityType': self.personality_type,
            'is_available': self.is_available,
            'isAvailable': self.is_available
        })
        return data

    def __repr__(self):
        return f'<Mentor {self.name} ({self.personality_type})>'
