"""
ZeX-ATS-AI Configuration Management
Handles all application settings and environment configuration.
"""

import os
from typing import List, Optional, Dict, Any
import json
from pathlib import Path
try:
    from pydantic_settings import BaseSettings  # type: ignore
    from pydantic import validator  # type: ignore
except Exception:  # lightweight fallback without pydantic
    class BaseSettings:  # type: ignore
        def __init__(self, **kwargs):
            for k,v in kwargs.items():
                setattr(self, k, v)
    def validator(*_args, **_kwargs):  # type: ignore
        def wrap(fn):
            return fn
        return wrap


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
    secret_key: str = "zex-ats-ai-secret-key-development-change-in-production"
    jwt_secret_key: str = "zex-ats-ai-jwt-secret-key-development-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = "sqlite:///./data/ats.db"
    redis_url: str = "redis://localhost:6379/0"
    
    # AI Services (external providers removed; placeholders intentionally omitted)
    
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
    supported_formats: List[str] = ["pdf", "docx", "txt", "jpg", "png", "pptx", "xlsx", "mp3", "mp4"]
    
    # AI Features
    enable_resume_scoring: bool = True
    enable_job_matching: bool = True
    enable_salary_prediction: bool = True
    enable_skills_extraction: bool = True
    enable_sentiment_analysis: bool = True
    # Dashboard user preference persistence
    preferences_file: str = "data/user_prefs.json"
    # Role defaults
    default_roles: List[str] = ["user", "admin"]
    default_role: str = "user"
    
    @validator('supported_formats', pre=True)
    def parse_supported_formats(cls, v):
        """Parse supported formats from string or list."""
        if isinstance(v, str):
            if v.lower() == "all":
                return ["pdf", "docx", "latex", "txt", "jpg", "jpeg", "png", "tiff", "pptx", "ppt", "xlsx", "xls", "mp3", "wav", "m4a", "mp4", "avi"]
            # Remove any brackets and quotes, then split by comma
            v = v.strip('[]"\'')
            return [fmt.strip().strip('"\'') for fmt in v.split(',') if fmt.strip()]
        elif isinstance(v, list):
            return v
        return ["pdf", "docx", "txt"]  # Default fallback
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


# ---------------------------------------------------------------------------
# User Preferences Persistence (simple JSON, no external dependencies)
# ---------------------------------------------------------------------------
_PREF_CACHE: Dict[str, Any] = {}
_PREFS_PATH = Path(settings.preferences_file)

def load_user_preferences() -> Dict[str, Any]:
    """Load user preferences from disk (cached)."""
    global _PREF_CACHE
    if _PREF_CACHE:
        return _PREF_CACHE
    try:
        if _PREFS_PATH.exists():
            with _PREFS_PATH.open('r', encoding='utf-8') as f:
                _PREF_CACHE = json.load(f)
        else:
            _PREF_CACHE = {}
    except Exception:
        _PREF_CACHE = {}
    return _PREF_CACHE

def save_user_preferences(prefs: Dict[str, Any]) -> None:
    """Persist user preferences to disk with atomic write."""
    global _PREF_CACHE
    _PREF_CACHE.update(prefs)
    try:
        _PREFS_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = _PREFS_PATH.with_suffix('.tmp')
        with tmp_path.open('w', encoding='utf-8') as f:
            json.dump(_PREF_CACHE, f, indent=2, ensure_ascii=False)
        tmp_path.replace(_PREFS_PATH)
    except Exception:
        pass

def get_user_preference(key: str, default: Any = None) -> Any:
    return load_user_preferences().get(key, default)

def set_user_preference(key: str, value: Any) -> None:
    save_user_preferences({key: value})

# ---------------------------------------------------------------------------
# Per-user (namespaced) preferences
# Stored under root dict as {"users": {user_id: {k:v}}}
# ---------------------------------------------------------------------------
def _ensure_users_root() -> Dict[str, Any]:
    prefs = load_user_preferences()
    if 'users' not in prefs or not isinstance(prefs['users'], dict):
        prefs['users'] = {}
        save_user_preferences({'users': prefs['users']})
    return prefs['users']

def get_user_scoped_preference(user_id: str, key: str, default: Any = None) -> Any:
    users = _ensure_users_root()
    return users.get(user_id, {}).get(key, default)

def set_user_scoped_preference(user_id: str, key: str, value: Any) -> None:
    users = _ensure_users_root()
    if user_id not in users or not isinstance(users[user_id], dict):
        users[user_id] = {}
    users[user_id][key] = value
    save_user_preferences({'users': users})

# ---------------------------------------------------------------------------
# Role-based persistence (simple; production would query DB)
# Stored as users[user_id]['roles'] = [role1, role2]
# ---------------------------------------------------------------------------
def get_user_roles(user_id: str) -> List[str]:
    users = _ensure_users_root()
    roles = users.get(user_id, {}).get('roles')
    if not roles:
        return [settings.default_role]
    if isinstance(roles, list):
        return [str(r) for r in roles]
    return [str(roles)]

def add_user_role(user_id: str, role: str) -> None:
    users = _ensure_users_root()
    entry = users.setdefault(user_id, {})
    existing = entry.get('roles') or []
    if role not in existing:
        entry['roles'] = existing + [role]
        save_user_preferences({'users': users})

def user_has_role(user_id: str, role: str) -> bool:
    return role in get_user_roles(user_id)

def require_role(user_id: str, role: str) -> bool:
    return user_has_role(user_id, role)


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


def get_settings():
    """Backward-compatible accessor for settings (unified main expects this)."""
    return settings
