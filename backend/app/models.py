"""
Database models for the agentic AI chatbot.
Defines all tables for conversations, messages, financial profiles, and vector search.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Integer, Float, Boolean
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    """User table for authentication and session management."""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)  # For future auth
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")

class Conversation(Base):
    """Conversation table to track chat sessions."""
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    title = Column(String(255), nullable=True)
    state = Column(String(50), default="active")  # active, paused, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    conversation_metadata = Column(JSON, default=dict)  # Additional conversation metadata
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    financial_profile = relationship("FinancialProfile", back_populates="conversation", uselist=False, cascade="all, delete-orphan")
    tool_calls = relationship("ToolCall", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    """Message table for storing chat messages."""
    __tablename__ = "messages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    sender = Column(String(20), nullable=False)  # user, bot, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message_type = Column(String(50), default="text")  # text, tool_call, tool_result, clarification
    message_metadata = Column(JSON, default=dict)  # Additional message metadata
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

class FinancialProfile(Base):
    """Financial profile table for storing user financial data."""
    __tablename__ = "financial_profiles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False, unique=True)
    profile_data = Column(JSON, nullable=False)  # Structured financial data
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completeness_score = Column(Float, default=0.0)  # 0-1 score of profile completeness
    
    # Relationships
    conversation = relationship("Conversation", back_populates="financial_profile")

class VectorChunk(Base):
    """Vector chunks table for semantic search capabilities."""
    __tablename__ = "vectors"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)  # Store as JSON string for SQLite compatibility
    source_type = Column(String(50), nullable=False)  # faq, knowledge_base, tool_output, conversation
    source_id = Column(String(255), nullable=True)  # Reference to original source
    chunk_metadata = Column(JSON, default=dict)  # Additional chunk metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<VectorChunk(id={self.id}, source_type='{self.source_type}')>"

class ToolCall(Base):
    """Tool call tracking for agent reasoning and debugging."""
    __tablename__ = "tool_calls"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    tool_name = Column(String(100), nullable=False)
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=True)
    status = Column(String(20), default="pending")  # pending, success, error
    error_message = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)  # Execution time in seconds
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="tool_calls")

# Helper functions for model operations
def create_financial_profile_data() -> Dict[str, Any]:
    """Create empty financial profile data structure."""
    return {
        "income": {
            "total": 0.0,
            "sources": {}
        },
        "expenses": {
            "recurring": {},
            "one_time": {}
        },
        "debts": {},
        "goals": {},
        "assets": {},
        "risk_tolerance": "moderate",
        "investment_experience": "beginner"
    }

def update_financial_profile(profile_data: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update financial profile with new data."""
    # Deep merge the updates
    for key, value in updates.items():
        if key in profile_data and isinstance(profile_data[key], dict) and isinstance(value, dict):
            profile_data[key].update(value)
        else:
            profile_data[key] = value
    
    # Recalculate totals
    if "income" in profile_data and "sources" in profile_data["income"]:
        profile_data["income"]["total"] = sum(profile_data["income"]["sources"].values())
    
    return profile_data 