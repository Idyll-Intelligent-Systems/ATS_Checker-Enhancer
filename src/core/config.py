"""
ZeX-ATS-AI Configuration Management
Handles all application settings and environment configuration.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Application Info
    app_name: str = "ZeX-ATS-AI"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # Security
    secret_key: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    
    # AI Services
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    
    # File Storage
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "zex-ats-documents"
    
    # Email & SMS
    sendgrid_api_key: Optional[str] = None
    from_email: str = "noreply@zex-ats-ai.com"
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    prometheus_port: int = 9090
    
    # Enterprise Features
    enable_analytics: bool = True
    enable_notifications: bool = True
    enable_reports: bool = True
    enable_multi_tenant: bool = True
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_hour: int = 1000
    
    # File Processing
    max_file_size_mb: int = 50
    supported_formats: List[str] = ["pdf", "doc", "docx", "txt"]
    
    # AI Features
    enable_resume_scoring: bool = True
    enable_job_matching: bool = True
    enable_salary_prediction: bool = True
    enable_skills_extraction: bool = True
    enable_sentiment_analysis: bool = True
    
    @validator('supported_formats', pre=True)
    def parse_supported_formats(cls, v):
        if isinstance(v, str):
            return [fmt.strip() for fmt in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_database_url() -> str:
    """Get database URL with fallback for testing."""
    if settings.database_url.startswith("sqlite"):
        return settings.database_url
    return settings.database_url


def get_redis_url() -> str:
    """Get Redis URL for caching."""
    return settings.redis_url


def is_production() -> bool:
    """Check if running in production mode."""
    return not settings.debug and os.getenv("ENVIRONMENT") == "production"


def get_cors_origins() -> List[str]:
    """Get CORS origins based on environment."""
    if is_production():
        return [
            "https://zex-ats-ai.com",
            "https://app.zex-ats-ai.com",
            "https://dashboard.zex-ats-ai.com"
        ]
    return ["*"]  # Allow all origins in development
