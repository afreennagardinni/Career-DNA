"""
Personality Drift Models
Enables tracking passive user engagement signals, calculating drift metrics,
administering micro-assessments, and logging long-term personality evolutions.
"""

from datetime import datetime
from app.extensions import db
from app.models.base import BaseModel


class PersonalitySignal(BaseModel):
    """
    PersonalitySignals: Logs passive engagement signals to detect evolving traits.
    Types: VideoSignal, QuizSignal, ContentLikeSignal, MentorTopicSignal
    """
    __tablename__ = 'personality_signals'

    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    signal_type = db.Column(db.String(100), nullable=False)  # VideoSignal, QuizSignal, etc.
    personality_type_indicated = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, default=1.0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    student = db.relationship('User', backref=db.backref('personality_signals', lazy='dynamic', cascade='all, delete-orphan'))

    # Compatibility properties for camelCase
    @property
    def studentId(self):
        return self.student_id

    @property
    def signalType(self):
        return self.signal_type

    @property
    def personalityTypeIndicated(self):
        return self.personality_type_indicated

    @property
    def createdAt(self):
        return self.created_at


class PersonalityDriftLog(BaseModel):
    """
    PersonalityDriftLog: Tracks calculated drift percentages per week.
    """
    __tablename__ = 'personality_drift_logs'

    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    week_of = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    dominant_signal_type = db.Column(db.String(100), nullable=False)  # dominant personality type
    drift_score = db.Column(db.Float, nullable=False)  # drift percentage (e.g. 45.5)
    consecutive_weeks = db.Column(db.Integer, default=1, nullable=False)
    drift_detected = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    student = db.relationship('User', backref=db.backref('drift_logs', lazy='dynamic', cascade='all, delete-orphan'))

    @property
    def studentId(self):
        return self.student_id

    @property
    def weekOf(self):
        return self.week_of

    @property
    def dominantSignalType(self):
        return self.dominant_signal_type

    @property
    def driftScore(self):
        return self.drift_score

    @property
    def consecutiveWeeks(self):
        return self.consecutive_weeks

    @property
    def driftDetected(self):
        return self.drift_detected


class MicroCheckIn(BaseModel):
    """
    MicroCheckIn: Logs targeted 5-question personality checks administered to verify drift.
    """
    __tablename__ = 'micro_check_ins'

    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    questions = db.Column(db.JSON, nullable=False)  # List of questions
    responses = db.Column(db.JSON, nullable=False)  # List of selected answers/scales
    result_type = db.Column(db.String(100), nullable=False)  # Personality type verified or "No Change"
    confirmed_drift = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    student = db.relationship('User', backref=db.backref('micro_check_ins', lazy='dynamic', cascade='all, delete-orphan'))

    @property
    def studentId(self):
        return self.student_id

    @property
    def confirmedDrift(self):
        return self.confirmed_drift

    @property
    def createdAt(self):
        return self.created_at


class PersonalityHistory(BaseModel):
    """
    PersonalityHistory: Historical record of a student's previous profiles.
    """
    __tablename__ = 'personality_histories'

    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    personality_type = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    reason = db.Column(db.String(100), default='drift_confirmed', nullable=False)

    # Relationships
    student = db.relationship('User', backref=db.backref('personality_history', lazy='dynamic', cascade='all, delete-orphan'))

    @property
    def studentId(self):
        return self.student_id

    @property
    def personalityType(self):
        return self.personality_type

    @property
    def startDate(self):
        return self.start_date

    @property
    def endDate(self):
        return self.end_date


class MentorHistory(BaseModel):
    """
    MentorHistory: Archive of previously assigned opposite mentors.
    """
    __tablename__ = 'mentor_histories'

    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentors.id', ondelete='CASCADE'), nullable=False)
    personality_type = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)

    # Relationships
    student = db.relationship('User', backref=db.backref('mentor_history', lazy='dynamic', cascade='all, delete-orphan'))
    mentor = db.relationship('Mentor')

    @property
    def studentId(self):
        return self.student_id

    @property
    def mentorId(self):
        return self.mentor_id

    @property
    def personalityType(self):
        return self.personality_type

    @property
    def startDate(self):
        return self.start_date

    @property
    def endDate(self):
        return self.end_date
