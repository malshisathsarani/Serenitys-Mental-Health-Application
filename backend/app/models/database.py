"""
Database Models for Serenity Mental Health Application
SQLAlchemy ORM models for MySQL database
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    """User model for storing user information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


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
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_conversation_timestamp', 'conversation_id', 'timestamp'),
        Index('idx_role', 'role'),
        Index('idx_crisis', 'crisis_detected'),
    )
    
    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', prediction='{self.prediction}')>"
