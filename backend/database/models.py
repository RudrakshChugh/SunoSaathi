"""
Database models for SunoSaathi
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model for storing user preferences"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True, nullable=False)
    preferred_language = Column(String(10), default="en")
    is_deaf = Column(Boolean, default=False)
    consent_camera = Column(Boolean, default=False)
    consent_microphone = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Session(Base):
    """Communication session between users"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user1_id = Column(String(100), nullable=False)
    user2_id = Column(String(100), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

class ConsentLog(Base):
    """Log of user consent for privacy compliance"""
    __tablename__ = "consent_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    consent_type = Column(String(50), nullable=False)  # camera, microphone
    granted = Column(Boolean, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    session_id = Column(String(100), nullable=True)

class SafetyLog(Base):
    """Log of safety filter actions"""
    __tablename__ = "safety_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False)
    user_id = Column(String(100), nullable=False)
    toxicity_score = Column(Float, nullable=False)
    was_blocked = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    # Note: We don't store the actual content for privacy

class SignDictionary(Base):
    """Dictionary of ISL signs with animation metadata"""
    __tablename__ = "sign_dictionary"
    
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(100), unique=True, index=True, nullable=False)
    language = Column(String(10), default="en")
    animation_file = Column(String(255), nullable=False)
    animation_metadata = Column(JSON, nullable=True)  # Duration, keyframes, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ISLGloss(Base):
    """Common ISL glosses for keyword mapping"""
    __tablename__ = "isl_glosses"
    
    id = Column(Integer, primary_key=True, index=True)
    gloss = Column(String(100), unique=True, index=True, nullable=False)
    keywords = Column(JSON, nullable=False)  # List of related keywords
    sign_id = Column(Integer, nullable=True)  # Reference to sign_dictionary
    created_at = Column(DateTime(timezone=True), server_default=func.now())
