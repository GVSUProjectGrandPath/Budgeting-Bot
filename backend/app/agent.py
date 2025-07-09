"""
Agentic AI system for the financial literacy chatbot.
Implements reasoning, tool use, and streaming capabilities.
"""

import asyncio
import json
import time
from typing import AsyncGenerator, Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import openai
from openai import AsyncOpenAI

from database import get_db_session
from models import Conversation, Message, FinancialProfile, VectorChunk, ToolCall
from tools import TOOL_REGISTRY, execute_tool, get_openai_function_schemas

logger = logging.getLogger(__name__)

# OpenAI client
client = AsyncOpenAI(
    api_key="your-openai-api-key",  # Set via environment variable
    base_url="http://localhost:11434/v1"  # Ollama endpoint
)

class AgentState:
    """Represents the current state of the agent during reasoning."""
    
    def __init__(self, conversation_id: str, user_message: str):
        self.conversation_id = conversation_id
        self.user_message = user_message
        self.context_messages: List[Dict[str, str]] = []
        self.tool_results: List[Dict[str, Any]] = []
        self.retrieved_chunks: List[Dict[str, Any]] = []
        self.current_step = 0
        self.max_steps = 5  # Prevent infinite loops
        self.start_time = time.time()
        
    def add_context_message(self, role: str, content: str):
        """Add a message to the context."""
        self.context_messages.append({"role": role, "content": content})
    
    def add_tool_result(self, tool_name: str, result: Dict[str, Any]):
        """Add a tool execution result."""
        self.tool_results.append({
            "tool": tool_name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_retrieved_chunk(self, chunk: Dict[str, Any]):
        """Add a retrieved knowledge chunk."""
        self.retrieved_chunks.append(chunk)
    
    def is_timeout(self) -> bool:
        """Check if agent has been running too long."""
        return time.time() - self.start_time > 30  # 30 second timeout
    
    def should_continue(self) -> bool:
        """Check if agent should continue reasoning."""
        return self.current_step < self.max_steps and not self.is_timeout()

class AgenticAI:
    """Main agentic AI system for financial literacy assistance."""
    
    def __init__(self):
        self.system_prompt = self._get_system_prompt()
        self.function_schemas = get_openai_function_schemas()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        return """You are pgpfinlitbot, a friendly and knowledgeable financial literacy assistant for students. You help users understand personal finance, budgeting, debt management, saving, and investing.

Your personality:
- Warm, encouraging, and educational
- Patient with beginners and clear in explanations
- Focus on building financial literacy skills
- Use real-world examples when helpful

Your capabilities:
- Answer financial questions directly
- Use specialized tools for calculations and analysis
- Access relevant financial information when needed
- Ask for clarification when necessary
- Use the user's financial profile for personalized advice

Available tools:
- generate_budget_sheet: Create personalized budget Excel files
- simulate_debt_payoff: Calculate debt payoff scenarios and interest savings
- calculate_savings_requirement: Determine monthly savings needed for goals
- calculate_financial_health_score: Assess overall financial health
- get_investment_recommendations: Provide personalized investment advice
- get_current_datetime: Get current date and time information
- get_general_info: Get general information about topics

Important guidelines:
1. Always respond naturally and conversationally
2. Don't repeat greetings if the conversation has already started
3. Use tools when calculations or analysis are needed
4. Provide clear, actionable advice
5. Be encouraging and supportive of financial goals
6. If you don't know something, be honest about it

Remember: You're having a natural conversation. Respond as a helpful financial advisor would, not as a system listing its capabilities."""

    async def process_user_message(
        self, 
        conversation_id: str, 
        user_message: str,
        user_name: str = "there"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process a user message through the agentic reasoning loop."""
        
        # Initialize agent state
        state = AgentState(conversation_id, user_message)
        
        # Save user message to database
        await self._save_message(conversation_id, "user", user_message)
        
        # Get conversation context
        context = await self._build_context(conversation_id, user_name)
        state.add_context_message("system", f"User: {user_name}")
        
        # Check if this is a simple question that can be answered directly
        simple_questions = ["date", "time", "today", "what day", "what time"]
        user_lower = user_message.lower().strip()
        
        # Check for simple date/time questions
        if any(question in user_lower for question in simple_questions):
            try:
                # Use the datetime tool directly
                result = await execute_tool("get_current_datetime", {"timezone": "UTC"})
                current_date = result["current_date"]
                current_time = result["current_time"]
                day_of_week = result["day_of_week"]
                
                response = f"Today is {day_of_week}, {current_date} at {current_time} UTC."
                await self._save_message(conversation_id, "bot", response)
                
                # Stream the response
                for char in response:
                    yield {"type": "token", "token": char}
                    await asyncio.sleep(0.01)
                return
                
            except Exception as e:
                logger.error(f"Error getting date/time: {e}")
        
        # Check for general questions
        general_keywords = ["hello", "hi", "help", "thanks", "thank you", "weather"]
        if any(keyword in user_lower for keyword in general_keywords):
            try:
                # Use the general info tool
                result = await execute_tool("get_general_info", {"topic": user_message})
                response = result["information"]
                await self._save_message(conversation_id, "bot", response)
                
                # Stream the response
                for char in response:
                    yield {"type": "token", "token": char}
                    await asyncio.sleep(0.01)
                return
                
            except Exception as e:
                logger.error(f"Error getting general info: {e}")
        
        # Agent reasoning loop (internal only)
        final_response = None
        while state.should_continue():
            state.current_step += 1
            
            # Build prompt for this reasoning step
            prompt = self._build_reasoning_prompt(state, context)
            
            try:
                # Get LLM response with function calling
                response = await self._get_llm_response(prompt, state, context)
                
                # Handle tool calls internally
                if response.get("tool_calls"):
                    for tool_call in response["tool_calls"]:
                        result = await self._execute_tool_call(tool_call, state)
                        state.add_tool_result(tool_call["name"], result)
                
                # Check if we have a final answer
                if response.get("final_answer"):
                    final_response = response["final_answer"]
                    break
                    
            except Exception as e:
                logger.error(f"Error in reasoning step {state.current_step}: {e}")
                final_response = f"I encountered an error while processing your request: {str(e)}"
                break
        
        # Handle timeout or max steps
        if not final_response:
            if not state.should_continue():
                final_response = "I've reached the maximum reasoning steps. Let me provide you with the best answer I can based on what I've analyzed."
            else:
                final_response = "I'm having trouble processing your request. Could you please rephrase your question or provide more details?"
        
        # Save final response to database
        await self._save_message(conversation_id, "bot", final_response)
        
        # Stream the final response to user
        for char in final_response:
            yield {"type": "token", "token": char}
            await asyncio.sleep(0.01)

    async def _build_context(self, conversation_id: str, user_name: str) -> Dict[str, Any]:
        """Build context from conversation history and financial profile."""
        async with get_db_session() as session:
            # Get recent messages
            messages_query = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(desc(Message.timestamp)).limit(10)
            
            messages_result = await session.execute(messages_query)
            recent_messages = messages_result.scalars().all()
            
            # Get financial profile
            profile_query = select(FinancialProfile).where(
                FinancialProfile.conversation_id == conversation_id
            )
            profile_result = await session.execute(profile_query)
            financial_profile = profile_result.scalar_one_or_none()
            
            # Convert messages to proper LLM format with alternating roles
            formatted_messages = []
            for msg in reversed(recent_messages):  # Reverse to get chronological order
                if msg.sender == "user":
                    formatted_messages.append({
                        "role": "user",
                        "content": msg.content
                    })
                elif msg.sender == "bot":
                    formatted_messages.append({
                        "role": "assistant", 
                        "content": msg.content
                    })
            
            return {
                "user_name": user_name,
                "recent_messages": [
                    {
                        "sender": msg.sender,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in recent_messages
                ],
                "formatted_messages": formatted_messages,  # For LLM context
                "financial_profile": financial_profile.profile_data if financial_profile else {},
                "profile_completeness": financial_profile.completeness_score if financial_profile else 0.0
            }

    def _build_reasoning_prompt(self, state: AgentState, context: Dict[str, Any]) -> str:
        """Build the prompt for the current reasoning step."""
        
        prompt = f"{self.system_prompt}\n\n"
        prompt += f"Current conversation context:\n"
        prompt += f"User: {context['user_name']}\n"
        prompt += f"Financial profile completeness: {context['profile_completeness']:.1%}\n\n"
        
        # Add recent conversation history
        if context["recent_messages"]:
            prompt += "Recent conversation:\n"
            for msg in context["recent_messages"][-5:]:  # Last 5 messages
                prompt += f"{msg['sender'].title()}: {msg['content']}\n"
            prompt += "\n"
        
        # Add financial profile summary
        if context["financial_profile"]:
            profile = context["financial_profile"]
            prompt += "Financial profile summary:\n"
            if profile.get("income", {}).get("total"):
                prompt += f"- Monthly income: ${profile['income']['total']:,.2f}\n"
            if profile.get("expenses", {}).get("recurring"):
                total_expenses = sum(profile["expenses"]["recurring"].values())
                prompt += f"- Monthly expenses: ${total_expenses:,.2f}\n"
            if profile.get("debts"):
                total_debt = sum(debt.get("balance", 0) for debt in profile["debts"].values())
                prompt += f"- Total debt: ${total_debt:,.2f}\n"
            prompt += "\n"
        
        # Add current user message
        prompt += f"Current user message: {state.user_message}\n\n"
        
        # Add tool results from previous steps
        if state.tool_results:
            prompt += "Previous tool results:\n"
            for result in state.tool_results:
                prompt += f"- {result['tool']}: {json.dumps(result['result'], indent=2)}\n"
            prompt += "\n"
        
        # Add retrieved knowledge
        if state.retrieved_chunks:
            prompt += "Relevant knowledge:\n"
            for chunk in state.retrieved_chunks:
                prompt += f"- {chunk['content']}\n"
            prompt += "\n"
        
        # Check if this is a new conversation or continuing one
        message_count = len(context.get("recent_messages", []))
        if message_count <= 2:  # Very new conversation
            prompt += "This appears to be the start of a conversation. Provide a warm, helpful response."
        else:
            prompt += "Continue the conversation naturally. Don't repeat greetings or introductions."
        
        prompt += "\n\nProvide a helpful, conversational response. If you need to use a tool, do so. If you have a complete answer, provide it directly."
        
        return prompt

    async def _get_llm_response(self, prompt: str, state: AgentState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get response from LLM with function calling."""
        
        messages = [
            {"role": "system", "content": prompt}
        ]
        
        # Add conversation history with proper roles
        if context.get("formatted_messages"):
            messages.extend(context["formatted_messages"])
        
        # Add context messages from current reasoning
        messages.extend(state.context_messages)
        
        try:
            response = await client.chat.completions.create(
                model="mistral:7b-instruct-q4_K_M",  # Using available Ollama model
                messages=messages,
                functions=self.function_schemas,
                function_call="auto",
                temperature=0.7,
                max_tokens=1000
            )
            
            message = response.choices[0].message
            result = {
                "content": message.content or "",
                "tool_calls": [],
                "final_answer": None
            }
            
            # Handle function calls
            if message.function_call:
                result["tool_calls"].append({
                    "name": message.function_call.name,
                    "arguments": json.loads(message.function_call.arguments)
                })
            
            # Check if this is a final answer
            if message.content and not message.function_call:
                result["final_answer"] = message.content
            
            return result
            
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            raise

    async def _execute_tool_call(self, tool_call: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        """Execute a tool call and save the result."""
        
        tool_name = tool_call["name"]
        tool_args = tool_call["arguments"]
        
        # Execute the tool
        start_time = time.time()
        try:
            result = await execute_tool(tool_name, tool_args)
            execution_time = time.time() - start_time
            
            # Save tool call to database
            await self._save_tool_call(
                state.conversation_id,
                tool_name,
                tool_args,
                result,
                execution_time
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_result = {"error": str(e)}
            
            # Save failed tool call
            await self._save_tool_call(
                state.conversation_id,
                tool_name,
                tool_args,
                error_result,
                execution_time,
                error_message=str(e)
            )
            
            raise

    async def _save_message(self, conversation_id: str, sender: str, content: str):
        """Save a message to the database."""
        async with get_db_session() as session:
            message = Message(
                conversation_id=conversation_id,
                sender=sender,
                content=content,
                timestamp=datetime.utcnow()
            )
            session.add(message)
            await session.commit()

    async def _save_tool_call(
        self,
        conversation_id: str,
        tool_name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        execution_time: float,
        error_message: Optional[str] = None
    ):
        """Save a tool call to the database."""
        async with get_db_session() as session:
            tool_call = ToolCall(
                conversation_id=conversation_id,
                tool_name=tool_name,
                input_data=input_data,
                output_data=output_data,
                status="error" if error_message else "success",
                error_message=error_message,
                execution_time=execution_time,
                timestamp=datetime.utcnow()
            )
            session.add(tool_call)
            await session.commit()

    async def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant knowledge chunks."""
        return await search_similar_chunks(query, limit)

    async def add_knowledge_chunk(
        self,
        content: str,
        source_type: str,
        source_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a new knowledge chunk to the vector store."""
        await add_chunk_to_vector_store(content, source_type, source_id, metadata) 