from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    api_v1_str: str = "/api/v1"
    project_name: str = "Credit Risk Assessment"
    
    # Database
    database_url: str = "sqlite:///./credit_risk.db"
    
    # Groq Settings
    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
    groq_model: str = "llama3-70b-8192"
    
    # MCP Settings
    mcp_server_url: str = "http://localhost:3001"
    
    # Quality Threshold
    quality_threshold: float = 0.8
    
    # Workflow Settings
    max_iterations: int = 5
    
    class Config:
        env_file = ".env"

settings = Settings()
