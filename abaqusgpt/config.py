"""Configuration management for AbaqusGPT."""

import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config(BaseModel):
    """Application configuration."""
    
    # LLM Settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    default_model: str = os.getenv("DEFAULT_MODEL", "gpt-4o")
    
    # Ollama Settings
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Paths
    knowledge_base_path: Path = Path(__file__).parent.parent / "knowledge_base"
    
    # Agent Settings
    max_retries: int = 3
    temperature: float = 0.1


# Global config instance
config = Config()
