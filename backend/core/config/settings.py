# core/config/settings.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Dict, Any
from pathlib import Path
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    # Application Settings
    PROJECT_NAME: str = "InsightFlow AI Analytics Tool"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")
    API_KEY: str = os.getenv("API_KEY", "")
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".csv"]
    
    # Model Settings
    MODEL_SETTINGS: Dict[str, Any] = {
        "temperature": 0.1,
        "max_retries": 3,
        "timeout": 45
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get singleton instance of Settings"""
    return Settings()

# Export the Settings class and get_settings function
__all__ = ["Settings", "get_settings"]