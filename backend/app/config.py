"""
Application configuration settings
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    environment: str = "development"
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Ollama Configuration
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_timeout: int = 30

    # Scanning Configuration
    max_scan_duration: int = 60
    rate_limit_per_ip: int = 10
    blocked_domains: List[str] = ["localhost", "127.0.0.1"]

    # External Services
    redis_url: str = "redis://localhost:6379"
    database_url: str = "sqlite:///./scanity.db"

    class Config:
        env_file = ".env"


settings = Settings()