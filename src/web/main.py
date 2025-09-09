"""
ZeX-ATS-AI Web Application
FastAPI-based enterprise web application with advanced features.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid
import json

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest
import structlog

from src.core.config import settings, get_cors_origins
from src.core.ats_analyzer import ATSAnalyzer, ResumeAnalysis
from src.core.resume_processor import ResumeProcessor
from src.database.models import User, Analysis, create_tables
from src.database.connection import get_database_session
from src.auth.jwt_handler import JWTHandler
from src.utils.rate_limiter import RateLimiter
from src.utils.cache_manager import CacheManager

# Initialize logger
logger = structlog.get_logger()

# Metrics
request_count = Counter('zex_ats_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('zex_ats_request_duration_seconds', 'Request duration')
analysis_count = Counter('zex_ats_analysis_total', 'Total analyses performed')

# Initialize FastAPI app
app = FastAPI(
    title="ZeX-ATS-AI",
    description="Enterprise-Grade ATS Checker & Enhancer",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Static files and templates
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
templates = Jinja2Templates(directory="src/web/templates")

# Security
security = HTTPBearer()

# Initialize components
ats_analyzer = ATSAnalyzer()
resume_processor = ResumeProcessor()
jwt_handler = JWTHandler()
rate_limiter = RateLimiter()
cache_manager = CacheManager()

# Pydantic models
class AnalyzeRequest(BaseModel):
    job_description: Optional[str] = None
    target_role: Optional[str] = None
    include_ai_insights: bool = True
    analysis_type: str = Field(default="comprehensive", pattern="^(basic|comprehensive|detailed)$")

class AnalyzeTextRequest(BaseModel):
    resume_text: str = Field(..., min_length=50, max_length=50000)
    job_description: Optional[str] = None
    target_role: Optional[str] = None
    include_ai_insights: bool = True

class UserRegistration(BaseModel):
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    organization: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class AnalysisHistory(BaseModel):
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

# Dependency functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user."""
    try:
        payload = jwt_handler.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Get user from database
        async with get_database_session() as session:
            user = await session.get(User, user_id)
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return user
    except Exception as e:
        logger.error("Authentication failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

async def check_rate_limit(user: User = Depends(get_current_user)):
    """Check rate limiting for user requests."""
    if not await rate_limiter.check_limit(user.id, user.subscription_tier):
        raise HTTPException(
            status_code=429, 
            detail="Rate limit exceeded. Please upgrade your plan or try again later."
        )
    return user

# Routes
@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with application overview."""
    return templates.TemplateResponse("index.html", {
        "request": {},
        "app_name": settings.app_name,
        "version": settings.app_version
    })

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": settings.app_version,
        "environment": "production" if not settings.debug else "development"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()

# Authentication routes
@app.post("/auth/register")
async def register_user(user_data: UserRegistration):
    """Register a new user."""
    try:
        async with get_database_session() as session:
            # Check if user already exists
            existing_user = await session.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="User already exists")
            
            # Create new user
            new_user = User(
                email=user_data.email,
                full_name=user_data.full_name,
                organization=user_data.organization,
                subscription_tier="free"
            )
            new_user.set_password(user_data.password)
            
            session.add(new_user)
            await session.commit()
            
            # Generate tokens
            access_token = jwt_handler.create_access_token({"sub": str(new_user.id)})
            
            logger.info("User registered", user_id=new_user.id, email=user_data.email)
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": new_user.id,
                    "email": new_user.email,
                    "full_name": new_user.full_name,
                    "subscription_tier": new_user.subscription_tier
                }
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("User registration failed", error=str(e))
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/auth/login")
async def login_user(login_data: UserLogin):
    """Authenticate user and return access token."""
    try:
        async with get_database_session() as session:
            user = await session.query(User).filter(User.email == login_data.email).first()
            if not user or not user.check_password(login_data.password):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Update last login
            user.last_login = datetime.utcnow()
            await session.commit()
            
            # Generate tokens
            access_token = jwt_handler.create_access_token({"sub": str(user.id)})
            
            logger.info("User logged in", user_id=user.id, email=login_data.email)
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "subscription_tier": user.subscription_tier
                }
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("User login failed", error=str(e))
        raise HTTPException(status_code=500, detail="Login failed")

# Analysis routes
@app.post("/analyze/file")
async def analyze_resume_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    target_role: Optional[str] = Form(None),
    include_ai_insights: bool = Form(True),
    user: User = Depends(check_rate_limit)
):
    """Analyze resume from uploaded file."""
    start_time = time.time()
    analysis_id = str(uuid.uuid4())
    
    try:
        request_count.labels(method="POST", endpoint="/analyze/file").inc()
        
        # Validate and process file
        file_content = await file.read()
        if not file_content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Process resume
        processed_resume = await resume_processor.process_resume_file(
            io.BytesIO(file_content), file.filename
        )
        
        # Perform ATS analysis
        analysis_result = await ats_analyzer.analyze_resume(
            processed_resume.cleaned_text,
            job_description,
            target_role
        )
        
        # Store analysis in database
        background_tasks.add_task(
            store_analysis_result,
            user.id,
            analysis_id,
            analysis_result,
            processed_resume.metadata,
            file.filename
        )
        
        # Update metrics
        analysis_count.inc()
        request_duration.observe(time.time() - start_time)
        
        logger.info(
            "File analysis completed",
            user_id=user.id,
            analysis_id=analysis_id,
            filename=file.filename,
            processing_time=time.time() - start_time
        )
        
        return {
            "analysis_id": analysis_id,
            "analysis": analysis_result.to_dict(),
            "file_metadata": processed_resume.metadata.to_dict(),
            "processing_time": time.time() - start_time
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("File analysis failed", error=str(e), analysis_id=analysis_id)
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.post("/analyze/text")
async def analyze_resume_text(
    background_tasks: BackgroundTasks,
    request_data: AnalyzeTextRequest,
    user: User = Depends(check_rate_limit)
):
    """Analyze resume from text input."""
    start_time = time.time()
    analysis_id = str(uuid.uuid4())
    
    try:
        request_count.labels(method="POST", endpoint="/analyze/text").inc()
        
        # Process resume text
        processed_resume = await resume_processor.process_resume_text(request_data.resume_text)
        
        # Perform ATS analysis
        analysis_result = await ats_analyzer.analyze_resume(
            processed_resume.cleaned_text,
            request_data.job_description,
            request_data.target_role
        )
        
        # Store analysis in database
        background_tasks.add_task(
            store_analysis_result,
            user.id,
            analysis_id,
            analysis_result,
            processed_resume.metadata,
            "text_input"
        )
        
        # Update metrics
        analysis_count.inc()
        request_duration.observe(time.time() - start_time)
        
        logger.info(
            "Text analysis completed",
            user_id=user.id,
            analysis_id=analysis_id,
            processing_time=time.time() - start_time
        )
        
        return {
            "analysis_id": analysis_id,
            "analysis": analysis_result.to_dict(),
            "processing_time": time.time() - start_time
        }
    
    except Exception as e:
        logger.error("Text analysis failed", error=str(e), analysis_id=analysis_id)
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.get("/analysis/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    user: User = Depends(get_current_user)
):
    """Get specific analysis result."""
    try:
        async with get_database_session() as session:
            analysis = await session.query(Analysis).filter(
                Analysis.id == analysis_id,
                Analysis.user_id == user.id
            ).first()
            
            if not analysis:
                raise HTTPException(status_code=404, detail="Analysis not found")
            
            return {
                "analysis": json.loads(analysis.result),
                "created_at": analysis.created_at,
                "filename": analysis.filename
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve analysis", error=str(e), analysis_id=analysis_id)
        raise HTTPException(status_code=500, detail="Failed to retrieve analysis")

@app.get("/analysis/history")
async def get_analysis_history(
    limit: int = 10,
    offset: int = 0,
    user: User = Depends(get_current_user)
):
    """Get user's analysis history."""
    try:
        async with get_database_session() as session:
            analyses = await session.query(Analysis).filter(
                Analysis.user_id == user.id
            ).order_by(Analysis.created_at.desc()).offset(offset).limit(limit).all()
            
            return {
                "analyses": [
                    {
                        "id": analysis.id,
                        "filename": analysis.filename,
                        "created_at": analysis.created_at,
                        "ats_score": json.loads(analysis.result)["ats_score"]["overall_score"]
                    }
                    for analysis in analyses
                ],
                "total": await session.query(Analysis).filter(Analysis.user_id == user.id).count()
            }
    
    except Exception as e:
        logger.error("Failed to retrieve analysis history", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve history")

@app.get("/user/profile")
async def get_user_profile(user: User = Depends(get_current_user)):
    """Get user profile information."""
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "organization": user.organization,
        "subscription_tier": user.subscription_tier,
        "created_at": user.created_at,
        "last_login": user.last_login,
        "analyses_count": user.analyses_count
    }

@app.get("/user/usage")
async def get_user_usage(user: User = Depends(get_current_user)):
    """Get user usage statistics."""
    current_usage = await rate_limiter.get_current_usage(user.id)
    limits = rate_limiter.get_tier_limits(user.subscription_tier)
    
    return {
        "current_usage": current_usage,
        "limits": limits,
        "subscription_tier": user.subscription_tier,
        "usage_percentage": (current_usage / limits["daily_limit"]) * 100 if limits["daily_limit"] > 0 else 0
    }

# Background tasks
async def store_analysis_result(
    user_id: str,
    analysis_id: str,
    analysis_result: ResumeAnalysis,
    metadata: Dict,
    filename: str
):
    """Store analysis result in database."""
    try:
        async with get_database_session() as session:
            analysis = Analysis(
                id=analysis_id,
                user_id=user_id,
                filename=filename,
                result=json.dumps(analysis_result.to_dict()),
                metadata=json.dumps(metadata.to_dict() if hasattr(metadata, 'to_dict') else metadata)
            )
            
            session.add(analysis)
            await session.commit()
            
            # Update user analysis count
            user = await session.get(User, user_id)
            if user:
                user.analyses_count += 1
                await session.commit()
            
            logger.info("Analysis stored", analysis_id=analysis_id, user_id=user_id)
    
    except Exception as e:
        logger.error("Failed to store analysis", error=str(e), analysis_id=analysis_id)

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting ZeX-ATS-AI application", version=settings.app_version)
    
    # Create database tables
    await create_tables()
    
    # Initialize cache
    await cache_manager.initialize()
    
    logger.info("Application startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on application shutdown."""
    logger.info("Shutting down ZeX-ATS-AI application")
    
    # Close cache connections
    await cache_manager.close()
    
    logger.info("Application shutdown completed")

# Run application
if __name__ == "__main__":
    uvicorn.run(
        "src.web.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers if not settings.debug else 1,
        reload=settings.debug
    )
