"""Configuration settings for the meal planner application."""

import os
import sys
from pathlib import Path
from typing import List, Optional, Union

from loguru import logger
from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from meal_planner.core.models import OCREngine


class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    app_name: str = "Meal Planner"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    # API settings
    api_port: int = 8000
    # Use string type to avoid Pydantic trying to parse as JSON
    _allowed_origins: str = "http://localhost:3000,http://localhost:8000,http://localhost:8080"
    
    # Database settings
    database_url: str = Field(default="sqlite+aiosqlite:///./data/meal_planner.db")
    
    # Data directories
    data_dir: Path = Field(default=Path("data"))
    upload_dir: Optional[Path] = Field(default=None)
    recipes_dir: Optional[Path] = Field(default=None)
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-this-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    
    # File upload - use simple types to avoid JSON parsing issues
    max_upload_size: int = Field(default=10 * 1024 * 1024)  # 10MB
    # Don't define allowed_extensions as a List in .env to avoid JSON parsing
    
    # OCR settings
    ocr_primary_engine: OCREngine = OCREngine.PYMUPDF
    ocr_fallback_engine: Optional[OCREngine] = OCREngine.MARKER
    
    # LLM settings
    llm_provider: str = "ollama"
    llm_model: str = "llama3"
    llm_api_base: str = "http://localhost:11434/api"
    llm_timeout: int = Field(default=30)
    
    # Caching
    cache_ttl: int = Field(default=300)  # 5 minutes
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=60)
    
    # Model config
    model_config = SettingsConfigDict(
        env_prefix="MEAL_PLANNER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    @property
    def allowed_origins(self) -> List[str]:
        """Parse allowed_origins from comma-separated string."""
        if isinstance(self._allowed_origins, str):
            return [origin.strip() for origin in self._allowed_origins.split(",") if origin.strip()]
        return ["http://localhost:3000", "http://localhost:8000", "http://localhost:8080"]
    
    @property
    def allowed_extensions(self) -> List[str]:
        """Return allowed file extensions."""
        return [".pdf", ".jpg", ".jpeg", ".png", ".txt"]
    
    def __init__(self, **kwargs):
        """Initialize settings."""
        super().__init__(**kwargs)
        
        # Set derived paths
        if self.upload_dir is None:
            self.upload_dir = self.data_dir / "uploads"
        
        if self.recipes_dir is None:
            self.recipes_dir = self.data_dir / "recipes"
        
        # Convert string paths to Path objects
        if isinstance(self.data_dir, str):
            self.data_dir = Path(self.data_dir)
        
        if isinstance(self.upload_dir, str):
            self.upload_dir = Path(self.upload_dir)
        
        if isinstance(self.recipes_dir, str):
            self.recipes_dir = Path(self.recipes_dir)


# Create settings instance
settings = Settings()

# Configure logger
logger.remove()
logger.add(
    sys.stderr,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)