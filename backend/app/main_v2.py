"""
pgpfinlitbot FastAPI Backend - Agentic AI System
Student finance chatbot with reasoning, tool use, and persistent memory.
"""

import asyncio
import json
import os
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Optional, Any, List
from datetime import datetime
import logging
from uuid import uuid4
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Import our new modules
from database import init_db, close_db, check_db_health, get_db_session
from models import Conversation, Message, FinancialProfile, User
from agent import AgenticAI
from tools import TOOL_REGISTRY, execute_tool

# Set up logger
logger = logging.getLogger("pgpfinlitbot")
logging.basicConfig(level=logging.INFO)

# Initialize agentic AI system
agent = AgenticAI()

# Pydantic models for API
class ChatRequest(BaseModel):
    msg: str
    user_name: str = "there"
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    database_healthy: bool
    agent_ready: bool
    timestamp: float

class ConversationData(BaseModel):
    id: str
    title: str
    created_at: str
    message_count: int
    financial_profile: Optional[Dict[str, Any]] = None

# Database session dependency
async def get_db():
    async with get_db_session() as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Starting pgpfinlitbot agentic AI system...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    # Knowledge base initialization removed for now
    logger.info("Knowledge base initialization skipped")
    
    logger.info("pgpfinlitbot agentic AI system ready!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down pgpfinlitbot...")
    await close_db()

# Create FastAPI app
app = FastAPI(
    title="pgpfinlitbot Agentic AI",
    description="Financial literacy chatbot with reasoning and tool use",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_healthy = await check_db_health()
    
    return HealthResponse(
        status="healthy" if db_healthy else "unhealthy",
        database_healthy=db_healthy,
        agent_ready=True,
        timestamp=time.time()
    )

@app.post("/chat")
async def chat_stream(request: ChatRequest):
    """Main chat endpoint with agentic AI processing."""
    
    # Validate input
    if not request.msg.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Get or create conversation
    conversation_id = request.conversation_id or str(uuid4())
    
    # Ensure conversation exists in database
    async with get_db_session() as session:
        # Check if conversation exists
        conv_query = select(Conversation).where(Conversation.id == conversation_id)
        conv_result = await session.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()
        
        if not conversation:
            # Create new conversation
            conversation = Conversation(
                id=conversation_id,
                title=f"Chat with {request.user_name}",
                state="active"
            )
            session.add(conversation)
            
            # Create financial profile
            profile = FinancialProfile(
                conversation_id=conversation_id,
                profile_data={
                    "income": {"total": 0.0, "sources": {}},
                    "expenses": {"recurring": {}, "one_time": {}},
                    "debts": {},
                    "goals": {},
                    "assets": {},
                    "risk_tolerance": "moderate",
                    "investment_experience": "beginner"
                },
                completeness_score=0.0
            )
            session.add(profile)
            await session.commit()
    
    # Process message through agentic AI
    async def agent_stream():
        try:
            async for event in agent.process_user_message(
                conversation_id=conversation_id,
                user_message=request.msg,
                user_name=request.user_name
            ):
                # Handle token streaming
                if event.get("type") == "token":
                    token = event.get("token", "")
                    yield f"data: {json.dumps({'token': token})}\n\n"
                    await asyncio.sleep(0.01)  # Small delay for streaming effect
                    
        except Exception as e:
            logger.error(f"Error in agent stream: {e}")
            error_content = f"I encountered an error: {str(e)}"
            for char in error_content:
                yield f"data: {json.dumps({'token': char})}\n\n"
                await asyncio.sleep(0.01)
    
    return StreamingResponse(
        agent_stream(),
        media_type="text/plain",
        headers={
            "X-Conversation-ID": conversation_id,
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

@app.get("/conversations")
async def get_conversations(db: AsyncSession = Depends(get_db)) -> List[ConversationData]:
    """Get all conversations."""
    query = select(Conversation).order_by(Conversation.updated_at.desc())
    result = await db.execute(query)
    conversations = result.scalars().all()
    
    conversation_data = []
    for conv in conversations:
        # Get message count
        msg_query = select(Message).where(Message.conversation_id == conv.id)
        msg_result = await db.execute(msg_query)
        message_count = len(msg_result.scalars().all())
        
        # Get financial profile
        profile_query = select(FinancialProfile).where(FinancialProfile.conversation_id == conv.id)
        profile_result = await db.execute(profile_query)
        profile = profile_result.scalar_one_or_none()
        
        conversation_data.append(ConversationData(
            id=str(conv.id),
            title=conv.title,
            created_at=conv.created_at.isoformat(),
            message_count=message_count,
            financial_profile=profile.profile_data if profile else None
        ))
    
    return conversation_data

@app.get("/conversation/{conversation_id}")
async def get_conversation_data(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Get conversation data including messages and financial profile."""
    
    # Get conversation
    conv_query = select(Conversation).where(Conversation.id == conversation_id)
    conv_result = await db.execute(conv_query)
    conversation = conv_result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages
    msg_query = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.timestamp)
    msg_result = await db.execute(msg_query)
    messages = msg_result.scalars().all()
    
    # Get financial profile
    profile_query = select(FinancialProfile).where(FinancialProfile.conversation_id == conversation_id)
    profile_result = await db.execute(profile_query)
    profile = profile_result.scalar_one_or_none()
    
    return {
        "conversation": {
            "id": str(conversation.id),
            "title": conversation.title,
            "state": conversation.state,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat()
        },
        "messages": [
            {
                "id": str(msg.id),
                "sender": msg.sender,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "message_type": msg.message_type
            }
            for msg in messages
        ],
        "financial_profile": profile.profile_data if profile else {},
        "profile_completeness": profile.completeness_score if profile else 0.0
    }

@app.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a conversation and all associated data."""
    
    # Get conversation
    conv_query = select(Conversation).where(Conversation.id == conversation_id)
    conv_result = await db.execute(conv_query)
    conversation = conv_result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Delete conversation (cascade will handle related data)
    await db.delete(conversation)
    await db.commit()
    
    return {"message": "Conversation deleted successfully"}

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download generated files (budgets, reports, etc.)."""
    file_path = Path(__file__).parent / "exports" / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )

@app.get("/tools")
async def get_available_tools():
    """Get list of available tools with their schemas."""
    tools = []
    for tool_name, tool_info in TOOL_REGISTRY.items():
        tools.append({
            "name": tool_name,
            "description": tool_info["description"],
            "input_schema": tool_info["input_schema"].model_json_schema(),
            "output_schema": tool_info["output_schema"].model_json_schema()
        })
    return {"tools": tools}

@app.post("/tools/{tool_name}/execute")
async def execute_tool_directly(tool_name: str, tool_args: Dict[str, Any]):
    """Execute a tool directly (for testing/debugging)."""
    if tool_name not in TOOL_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    try:
        result = await execute_tool(tool_name, tool_args)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Tool execution failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "pgpfinlitbot Agentic AI System",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/chat",
            "conversations": "/conversations",
            "health": "/health",
            "tools": "/tools"
        }
    }

@app.exception_handler(Exception)
async def internal_error(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main_v2:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 