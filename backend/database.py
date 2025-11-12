
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
db = SQLAlchemy()
class User(db.Model):
    """User account model"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    behavioral_profiles = db.relationship('BehavioralProfile', backref='user', cascade='all, delete-orphan')
    sessions = db.relationship('Session', backref='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
class BehavioralProfile(db.Model):
    """Stores behavioral biometric baseline for each user"""
    __tablename__ = 'behavioral_profiles'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    avg_typing_speed = db.Column(db.Float, default=0.0)
    avg_dwell_time = db.Column(db.Float, default=0.0)
    avg_flight_time = db.Column(db.Float, default=0.0)
    typing_std_dev = db.Column(db.Float, default=0.0)
    
    avg_mouse_speed = db.Column(db.Float, default=0.0)
    avg_acceleration = db.Column(db.Float, default=0.0)
    mouse_std_dev = db.Column(db.Float, default=0.0)
    
    preferred_paths = db.Column(db.String(1000), default='')
    
    samples_collected = db.Column(db.Integer, default=0)
    model_confidence = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BehavioralProfile user_id={self.user_id}>'

class Session(db.Model):
    """Tracks active user sessions with continuous auth"""
    __tablename__ = 'sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    logout_time = db.Column(db.DateTime, nullable=True)
    
    current_confidence = db.Column(db.Float, default=100.0)
    min_confidence = db.Column(db.Float, default=100.0)
    anomaly_count = db.Column(db.Integer, default=0)
    
    device_fingerprint = db.Column(db.String(255), default='')
    location_hash = db.Column(db.String(255), default='')
    
    is_active = db.Column(db.Boolean, default=True)
    is_compromised = db.Column(db.Boolean, default=False)
    
    behavioral_events = db.relationship('BehavioralEvent', backref='session', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Session user_id={self.user_id} active={self.is_active}>'

class BehavioralEvent(db.Model):
    """Individual behavioral events during a session"""
    __tablename__ = 'behavioral_events'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('sessions.id'), nullable=False, index=True)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    event_type = db.Column(db.String(50), nullable=False)
    
    keystroke_dwell_time = db.Column(db.Float, nullable=True)
    keystroke_flight_time = db.Column(db.Float, nullable=True)
    keystroke_pressure = db.Column(db.Float, nullable=True)
    
    mouse_x = db.Column(db.Float, nullable=True)
    mouse_y = db.Column(db.Float, nullable=True)
    mouse_speed = db.Column(db.Float, nullable=True)
    mouse_acceleration = db.Column(db.Float, nullable=True)
    click_type = db.Column(db.String(20), nullable=True)
    
    page_source = db.Column(db.String(255), nullable=True)
    page_destination = db.Column(db.String(255), nullable=True)
    time_on_page = db.Column(db.Float, nullable=True)
    
    anomaly_score = db.Column(db.Float, default=0.0)
    is_anomalous = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<BehavioralEvent type={self.event_type} anomaly={self.is_anomalous}>'
class AnomalyAlert(db.Model):
    """Logs anomaly detections and alerts"""
    __tablename__ = 'anomaly_alerts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('sessions.id'), nullable=False)
    
    alert_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    anomaly_score = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<AnomalyAlert {self.alert_type} severity={self.severity}>'
