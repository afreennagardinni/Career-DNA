"""
Video Model
Represents a video in the Career DNA platform.
"""

from app.extensions import db
from app.models.base import BaseModel


class Video(BaseModel):
    """
    Video model for storing curated videos.
    """
    
    __tablename__ = 'videos'
    
    title = db.Column(db.String(255), nullable=False)
    channel = db.Column(db.String(150))
    url = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.String(50))
    why = db.Column(db.Text)
    thumbnail = db.Column(db.String(255))
    
    # Required for personalised content engine
    personality_tags = db.Column(db.JSON, nullable=False)  # Array of strings
    
    # Properties for camelCase support
    @property
    def personalityTags(self):
        return self.personality_tags
    
    @personalityTags.setter
    def personalityTags(self, value):
        self.personality_tags = value
        
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'title': self.title,
            'channel': self.channel,
            'url': self.url,
            'duration': self.duration,
            'why': self.why,
            'thumbnail': self.thumbnail,
            'personality_tags': self.personality_tags,
            'personalityTags': self.personality_tags
        })
        return data

    def __repr__(self):
        return f'<Video {self.title}>'
