"""
ZeX-ATS-AI Database Models
SQLAlchemy models for enterprise data management.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import hashlib
import bcrypt

Base = declarative_base()


class User(Base):
    """User model for authentication and user management."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=True)
    subscription_tier = Column(String(50), default="free", nullable=False)  # free, pro, enterprise
    
    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Usage tracking
    analyses_count = Column(Integer, default=0, nullable=False)
    total_uploads = Column(Integer, default=0, nullable=False)
    storage_used = Column(Integer, default=0, nullable=False)  # in bytes
    
    # Subscription details
    subscription_start = Column(DateTime, nullable=True)
    subscription_end = Column(DateTime, nullable=True)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password: str) -> None:
        """Hash and set user password."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            'id': str(self.id),
            'email': self.email,
            'full_name': self.full_name,
            'organization': self.organization,
            'subscription_tier': self.subscription_tier,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'analyses_count': self.analyses_count,
            'total_uploads': self.total_uploads
        }


class Analysis(Base):
    """Analysis model for storing resume analysis results."""
    
    __tablename__ = "analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # File information
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=True)  # SHA-256 hash for deduplication
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(20), nullable=True)
    
    # Analysis details
    analysis_type = Column(String(50), default="comprehensive", nullable=False)
    job_description_provided = Column(Boolean, default=False, nullable=False)
    target_role = Column(String(255), nullable=True)
    
    # Results
    result = Column(JSON, nullable=False)  # Main analysis results
    metadata = Column(JSON, nullable=True)  # Processing metadata
    
    # Scores (for easy querying)
    overall_score = Column(Float, nullable=True)
    keyword_score = Column(Float, nullable=True)
    format_score = Column(Float, nullable=True)
    
    # Processing information
    processing_time = Column(Float, nullable=True)  # in seconds
    ai_insights_included = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    feedback = relationship("AnalysisFeedback", back_populates="analysis", cascade="all, delete-orphan")
    
    def to_dict(self) -> dict:
        """Convert analysis to dictionary."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'filename': self.filename,
            'analysis_type': self.analysis_type,
            'overall_score': self.overall_score,
            'keyword_score': self.keyword_score,
            'format_score': self.format_score,
            'processing_time': self.processing_time,
            'created_at': self.created_at,
            'result': self.result
        }


class AnalysisFeedback(Base):
    """User feedback on analysis results."""
    
    __tablename__ = "analysis_feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Feedback details
    rating = Column(Integer, nullable=False)  # 1-5 stars
    helpful = Column(Boolean, nullable=True)
    accurate = Column(Boolean, nullable=True)
    comments = Column(Text, nullable=True)
    
    # Specific feedback
    suggestions_helpful = Column(Boolean, nullable=True)
    score_accurate = Column(Boolean, nullable=True)
    would_recommend = Column(Boolean, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="feedback")
    user = relationship("User")


class APIKey(Base):
    """API keys for programmatic access."""
    
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    name = Column(String(255), nullable=False)  # User-friendly name
    key_hash = Column(String(64), nullable=False, unique=True)  # Hashed API key
    key_prefix = Column(String(10), nullable=False)  # First few chars for identification
    
    # Permissions and limits
    permissions = Column(JSON, default=lambda: ["analyze"], nullable=False)
    rate_limit = Column(Integer, default=1000, nullable=False)  # requests per day
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_used = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    @classmethod
    def generate_key(cls) -> str:
        """Generate a new API key."""
        return f"zex_{''.join(str(uuid.uuid4()).split('-'))}"
    
    def set_key(self, key: str) -> None:
        """Hash and set API key."""
        self.key_hash = hashlib.sha256(key.encode()).hexdigest()
        self.key_prefix = key[:8]
    
    def verify_key(self, key: str) -> bool:
        """Verify API key."""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return key_hash == self.key_hash


class UsageLog(Base):
    """Log of user activities for analytics and billing."""
    
    __tablename__ = "usage_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Activity details
    action = Column(String(100), nullable=False)  # analyze_file, analyze_text, etc.
    resource = Column(String(100), nullable=True)  # filename, analysis_id, etc.
    
    # Request details
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    api_key_id = Column(UUID(as_uuid=True), nullable=True)  # If via API
    
    # Processing details
    processing_time = Column(Float, nullable=True)
    file_size = Column(Integer, nullable=True)
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Billing information
    credits_used = Column(Integer, default=1, nullable=False)
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="usage_logs")


class SystemSettings(Base):
    """System-wide configuration settings."""
    
    __tablename__ = "system_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    key = Column(String(100), unique=True, nullable=False)
    value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    
    # Metadata
    created_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class AnalyticsEvent(Base):
    """Analytics events for business intelligence."""
    
    __tablename__ = "analytics_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Event details
    event_type = Column(String(100), nullable=False, index=True)  # user_registered, analysis_completed, etc.
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    
    # Event data
    properties = Column(JSON, nullable=True)  # Event-specific data
    
    # Context
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    referer = Column(String(500), nullable=True)


class JobDescription(Base):
    """Store job descriptions for analysis and trends."""
    
    __tablename__ = "job_descriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Job details
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True, index=True)
    location = Column(String(255), nullable=True)
    
    # Content
    description = Column(Text, nullable=False)
    requirements = Column(JSON, nullable=True)  # Extracted requirements
    keywords = Column(JSON, nullable=True)  # Extracted keywords
    
    # Analysis
    difficulty_level = Column(String(20), nullable=True)  # entry, mid, senior
    salary_range = Column(JSON, nullable=True)  # min, max, currency
    
    # Usage
    usage_count = Column(Integer, default=0, nullable=False)
    last_used = Column(DateTime, nullable=True)
    
    # Metadata
    source = Column(String(100), nullable=True)  # linkedin, indeed, manual, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# Database initialization functions
async def create_tables():
    """Create all database tables."""
    from src.database.connection import engine
    Base.metadata.create_all(bind=engine)


async def drop_tables():
    """Drop all database tables (use with caution)."""
    from src.database.connection import engine
    Base.metadata.drop_all(bind=engine)


# Index definitions for performance
def create_indexes():
    """Create additional database indexes for performance."""
    from sqlalchemy import Index
    
    # Composite indexes for common queries
    Index('idx_analyses_user_created', Analysis.user_id, Analysis.created_at)
    Index('idx_usage_logs_user_timestamp', UsageLog.user_id, UsageLog.timestamp)
    Index('idx_analytics_events_type_timestamp', AnalyticsEvent.event_type, AnalyticsEvent.timestamp)
    
    # Full-text search indexes (PostgreSQL specific)
    # These would be created with raw SQL in a migration
    pass
