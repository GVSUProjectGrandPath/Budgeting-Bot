"""
Vector search module for semantic retrieval using pgvector.
Handles embedding generation, storage, and similarity search.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session
from models import VectorChunk

# Initialize sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight model for embeddings

async def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a text string."""
    try:
        # Generate embedding
        embedding = model.encode(text)
        return embedding.tolist()
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # Return zero vector as fallback
        return [0.0] * 384  # Model dimension

async def add_chunk_to_vector_store(
    content: str,
    source_type: str,
    source_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Add a new knowledge chunk to the vector store."""
    
    # Generate embedding
    embedding = await generate_embedding(content)
    
    # Create vector chunk
    chunk = VectorChunk(
        content=content,
        embedding=embedding,
        source_type=source_type,
        source_id=source_id,
        metadata=metadata or {}
    )
    
    # Save to database
    async with get_db_session() as session:
        session.add(chunk)
        await session.commit()
        
    return str(chunk.id)

async def search_similar_chunks(
    query: str,
    limit: int = 5,
    similarity_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """Search for similar chunks using cosine similarity."""
    
    # Generate query embedding
    query_embedding = await generate_embedding(query)
    
    async with get_db_session() as session:
        # Search using cosine similarity
        # Note: This is a simplified version. In production, you'd use pgvector's cosine similarity
        query_stmt = select(VectorChunk).order_by(
            func.cosine_similarity(VectorChunk.embedding, query_embedding).desc()
        ).limit(limit)
        
        result = await session.execute(query_stmt)
        chunks = result.scalars().all()
        
        # Convert to dict format
        results = []
        for chunk in chunks:
            # Calculate similarity score (simplified)
            similarity = calculate_cosine_similarity(query_embedding, chunk.embedding)
            
            if similarity >= similarity_threshold:
                results.append({
                    "id": str(chunk.id),
                    "content": chunk.content,
                    "source_type": chunk.source_type,
                    "source_id": chunk.source_id,
                    "similarity": similarity,
                    "metadata": chunk.metadata
                })
        
        return results

def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    try:
        vec1_array = np.array(vec1)
        vec2_array = np.array(vec2)
        
        # Normalize vectors
        norm1 = np.linalg.norm(vec1_array)
        norm2 = np.linalg.norm(vec2_array)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Calculate cosine similarity
        similarity = np.dot(vec1_array, vec2_array) / (norm1 * norm2)
        return float(similarity)
    except Exception as e:
        print(f"Error calculating cosine similarity: {e}")
        return 0.0

async def initialize_knowledge_base():
    """Initialize the knowledge base with default financial literacy content."""
    
    # Default knowledge chunks
    knowledge_chunks = [
        {
            "content": "Budgeting is the foundation of financial health. Start by tracking your income and expenses, then create a plan that allocates your money to different categories like housing, food, transportation, and savings.",
            "source_type": "knowledge_base",
            "source_id": "budgeting_basics",
            "metadata": {"category": "budgeting", "difficulty": "beginner"}
        },
        {
            "content": "Student loans are a common form of debt for college students. Federal student loans typically have lower interest rates and more flexible repayment options than private loans. Always understand the terms before borrowing.",
            "source_type": "knowledge_base",
            "source_id": "student_loans",
            "metadata": {"category": "debt", "difficulty": "beginner"}
        },
        {
            "content": "Building credit is important for future financial opportunities. Start with a secured credit card or become an authorized user on a parent's card. Always pay bills on time and keep credit utilization low.",
            "source_type": "knowledge_base",
            "source_id": "credit_building",
            "metadata": {"category": "credit", "difficulty": "beginner"}
        },
        {
            "content": "Emergency funds should cover 3-6 months of living expenses. Start by saving a small amount each month and gradually build up your fund. This provides financial security for unexpected expenses.",
            "source_type": "knowledge_base",
            "source_id": "emergency_funds",
            "metadata": {"category": "saving", "difficulty": "beginner"}
        },
        {
            "content": "Compound interest is when you earn interest on both your principal and accumulated interest. The earlier you start investing, the more time your money has to grow through compound interest.",
            "source_type": "knowledge_base",
            "source_id": "compound_interest",
            "metadata": {"category": "investing", "difficulty": "intermediate"}
        },
        {
            "content": "Diversification is a key investment principle. Don't put all your money in one investment. Spread your money across different types of investments to reduce risk.",
            "source_type": "knowledge_base",
            "source_id": "diversification",
            "metadata": {"category": "investing", "difficulty": "intermediate"}
        },
        {
            "content": "The 50/30/20 rule is a simple budgeting guideline: 50% for needs (housing, food, utilities), 30% for wants (entertainment, dining out), and 20% for savings and debt repayment.",
            "source_type": "knowledge_base",
            "source_id": "50_30_20_rule",
            "metadata": {"category": "budgeting", "difficulty": "beginner"}
        },
        {
            "content": "Credit scores range from 300-850. A score above 700 is generally considered good. Factors affecting your score include payment history, credit utilization, length of credit history, and types of credit used.",
            "source_type": "knowledge_base",
            "source_id": "credit_scores",
            "metadata": {"category": "credit", "difficulty": "beginner"}
        },
        {
            "content": "ROTH IRA is a retirement account where you contribute after-tax money and withdrawals in retirement are tax-free. It's particularly beneficial for young people who expect to be in a higher tax bracket later.",
            "source_type": "knowledge_base",
            "source_id": "roth_ira",
            "metadata": {"category": "investing", "difficulty": "intermediate"}
        },
        {
            "content": "Debt-to-income ratio is calculated by dividing your monthly debt payments by your monthly income. Lenders prefer a ratio below 43%. Lower ratios indicate better financial health.",
            "source_type": "knowledge_base",
            "source_id": "debt_to_income",
            "metadata": {"category": "debt", "difficulty": "intermediate"}
        }
    ]
    
    # Add chunks to vector store
    for chunk_data in knowledge_chunks:
        await add_chunk_to_vector_store(
            content=chunk_data["content"],
            source_type=chunk_data["source_type"],
            source_id=chunk_data["source_id"],
            metadata=chunk_data["metadata"]
        )
    
    print(f"Initialized knowledge base with {len(knowledge_chunks)} chunks")

async def get_chunk_by_id(chunk_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific chunk by ID."""
    async with get_db_session() as session:
        query = select(VectorChunk).where(VectorChunk.id == chunk_id)
        result = await session.execute(query)
        chunk = result.scalar_one_or_none()
        
        if chunk:
            return {
                "id": str(chunk.id),
                "content": chunk.content,
                "source_type": chunk.source_type,
                "source_id": chunk.source_id,
                "metadata": chunk.metadata,
                "created_at": chunk.created_at.isoformat()
            }
        return None

async def delete_chunk(chunk_id: str) -> bool:
    """Delete a chunk from the vector store."""
    async with get_db_session() as session:
        query = select(VectorChunk).where(VectorChunk.id == chunk_id)
        result = await session.execute(query)
        chunk = result.scalar_one_or_none()
        
        if chunk:
            await session.delete(chunk)
            await session.commit()
            return True
        return False

async def get_chunks_by_source_type(source_type: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get chunks by source type."""
    async with get_db_session() as session:
        query = select(VectorChunk).where(
            VectorChunk.source_type == source_type
        ).limit(limit)
        
        result = await session.execute(query)
        chunks = result.scalars().all()
        
        return [
            {
                "id": str(chunk.id),
                "content": chunk.content,
                "source_type": chunk.source_type,
                "source_id": chunk.source_id,
                "metadata": chunk.metadata,
                "created_at": chunk.created_at.isoformat()
            }
            for chunk in chunks
        ] 