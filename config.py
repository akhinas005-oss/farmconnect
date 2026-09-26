from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os

class Settings(BaseSettings):
    APP_NAME: str = "FarmConnect API"
    ENV: str = "development"
    PORT: int = 8000
    HOST: str = "127.0.0.1"
    
    # Database Configuration
    DB_PATH: str = os.path.join(os.path.dirname(__file__), "farmconnect.db")
    
    # LLM API Secrets
    GEMINI_API_KEY: Optional[str] = None
    
    # CORS Origins
    # Restrict to explicit origins in production (e.g., ["https://farmconnect.app"])
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "*"  # Development fallback
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
