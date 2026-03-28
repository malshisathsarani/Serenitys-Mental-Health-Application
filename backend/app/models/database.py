"""
Database Models for Serenity Mental Health Application
SQLAlchemy ORM models for MySQL database
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Index, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    """User model for storing user information and authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # bcrypt hashed password
    full_name = Column(String(255), nullable=True)  # Optional profile info
    is_active = Column(Boolean, default=True)  # Account status
    is_verified = Column(Boolean, default=False)  # Email verification
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)  # Track user activity
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes for auth performance
    __table_args__ = (
        Index('idx_email_active', 'email', 'is_active'),
        Index('idx_username_active', 'username', 'is_active'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"


class Conversation(Base):
    """Conversation model for storing chat sessions"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), default="New Conversation")
    started_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    message_count = Column(Integer, default=0)
    crisis_detected = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_active', 'user_id', 'is_active'),
        Index('idx_last_message', 'last_message_at'),
    )
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}', messages={self.message_count})>"


class Message(Base):
    """Message model for storing individual chat messages"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # ML Analysis fields
    prediction = Column(String(50), nullable=True)  # Anxiety, Depression, Normal, Suicidal
    probabilities = Column(JSON, nullable=True)  # Store prediction probabilities
    crisis_detected = Column(Boolean, default=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    feedback_entries = relationship(
        "MessageFeedback",
        back_populates="message",
        cascade="all, delete-orphan",
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_conversation_timestamp', 'conversation_id', 'timestamp'),
        Index('idx_role', 'role'),
        Index('idx_crisis', 'crisis_detected'),
    )
    
    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', prediction='{self.prediction}')>"


class MessageFeedback(Base):
    """User feedback on assistant responses."""
    __tablename__ = "message_feedback"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    helpful = Column(Boolean, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    message = relationship("Message", back_populates="feedback_entries")
    user = relationship("User")

    __table_args__ = (
        Index("idx_feedback_message_user", "message_id", "user_id"),
        Index("idx_feedback_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<MessageFeedback(id={self.id}, message_id={self.message_id}, helpful={self.helpful})>"


class EmergencyContact(Base):
    """Emergency contacts for users - who to call in crisis situations"""
    __tablename__ = "emergency_contacts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)  # Contact name or title
    phone_number = Column(String(20), nullable=False)  # E.164 format: +1234567890
    contact_relationship = Column(String(100), nullable=True)  # e.g., "Mom", "Therapist", "Friend"
    is_hotline = Column(Boolean, default=False)  # True for crisis hotlines (988, etc.)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")

    __table_args__ = (
        Index("idx_user_emergency_contact", "user_id", "is_active"),
    )

    def __repr__(self):
        return f"<EmergencyContact(id={self.id}, name='{self.name}', is_hotline={self.is_hotline})>"


class EmergencyCall(Base):
    """Log of emergency calls made - for audit trail and analytics"""
    __tablename__ = "emergency_calls"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    emergency_contact_id = Column(Integer, ForeignKey("emergency_contacts.id", ondelete="SET NULL"), nullable=True)
    
    # Call details
    phone_number = Column(String(20), nullable=False)  # Target phone number
    call_sid = Column(String(100), nullable=True)  # Twilio Call SID for tracking
    status = Column(String(50), default="initiated")  # initiated, ringing, answered, completed, failed
    
    # Crisis context
    crisis_type = Column(String(100), nullable=True)  # Suicidal, Severe Depression, etc.
    fused_risk_score = Column(Float, nullable=True)  # Risk score that triggered the call
    text_risk_score = Column(Float, nullable=True)
    voice_risk_score = Column(Float, nullable=True)
    
    # Metadata
    reason = Column(String(255), nullable=True)  # Why the call was triggered
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)  # Associated message
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    call_initiated_at = Column(DateTime, nullable=True)
    call_completed_at = Column(DateTime, nullable=True)
    
    # Additional data
    call_metadata = Column(JSON, nullable=True)  # Store additional Twilio info

    user = relationship("User")
    conversation = relationship("Conversation")

    __table_args__ = (
        Index("idx_emergency_call_user", "user_id", "created_at"),
        Index("idx_emergency_call_status", "status"),
        Index("idx_emergency_call_crisis", "user_id", "fused_risk_score"),
    )

    def __repr__(self):
        return f"<EmergencyCall(id={self.id}, status='{self.status}', risk_score={self.fused_risk_score})>"
