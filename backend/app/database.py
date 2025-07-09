"""
Database configuration and connection management for the agentic AI chatbot.
Uses PostgreSQL with pgvector extension for semantic search capabilities.
"""

import os
import asyncio
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
from contextlib import asynccontextmanager

# Database configuration - Using SQLite for testing
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite+aiosqlite:///./pgpbot_test.db"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session with automatic cleanup."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize the database with all tables."""
    async with engine.begin() as conn:
        # Import and create all tables
        from models import (
            Conversation, Message, FinancialProfile, 
            VectorChunk, User, ToolCall
        )
        await conn.run_sync(Base.metadata.create_all)
        
        # Create basic indexes for performance (SQLite compatible)
        from sqlalchemy import text
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
            ON messages(conversation_id);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
            ON messages(timestamp);
        """))

async def close_db():
    """Close database connections."""
    await engine.dispose()

# Health check function
async def check_db_health() -> bool:
    """Check if database is accessible and healthy."""
    try:
        async with get_db_session() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False 