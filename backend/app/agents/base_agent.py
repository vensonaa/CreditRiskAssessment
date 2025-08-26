from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings
import uuid
from datetime import datetime

class BaseAgent(ABC):
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.llm = ChatGroq(
            model=settings.groq_model,
            temperature=0.1,
            api_key=settings.groq_api_key
        )
        self.conversation_history = []
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return agent response"""
        pass
    
    def add_to_history(self, message: str, role: str = "user"):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": message,
            "timestamp": datetime.now()
        })
    
    def get_system_prompt(self) -> str:
        """Get system prompt for the agent"""
        return f"You are a {self.agent_type} agent in a credit risk assessment system."
    
    async def generate_response(self, messages: list) -> str:
        """Generate response using LLM"""
        try:
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def create_request_id(self) -> str:
        """Create unique request ID"""
        return str(uuid.uuid4())
