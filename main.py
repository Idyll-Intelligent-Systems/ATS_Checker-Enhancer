"""
ZeX-ATS-AI FastAPI Application - Enhanced Multi-Format Support
Advanced ATS Resume Analyzer with comprehensive document processing capabilities.
"""

import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import time
import os
from pathlib import Path

# Import routers and dependencies
from src.api.v1 import analyze
from src.core.config import get_settings
from src.core.logging import setup_logging
from src.database.connection import get_database
from src.utils.health_check import HealthChecker
from src.schemas.analysis import ErrorResponse

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("🚀 Starting ZeX-ATS-AI Enhanced Multi-Format Platform...")
    
    # Initialize database
    try:
        database = get_database()
        await database.connect()
        logger.info("📊 Database connected successfully")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
    
    # Initialize health checker
    health_checker = HealthChecker()
    app.state.health_checker = health_checker
    
    # Log supported formats
    from src.ai.processors.enhanced_document_processor import EnhancedDocumentProcessor
    processor = EnhancedDocumentProcessor()
    supported_formats = list(processor.SUPPORTED_FORMATS.keys())
    logger.info(f"📄 Supported formats: {', '.join(supported_formats)}")
    
    logger.info("✅ ZeX-ATS-AI Platform started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down ZeX-ATS-AI Platform...")
    try:
        await database.disconnect()
        logger.info("📊 Database disconnected")
    except Exception as e:
        logger.error(f"❌ Database disconnection error: {e}")
    
    logger.info("✅ ZeX-ATS-AI Platform shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="ZeX-ATS-AI Enhanced Multi-Format Platform",
    description="""
    ## 🎯 Advanced ATS Resume Analyzer with Multi-Format Support

    **ZeX-ATS-AI** is a comprehensive resume analysis platform that supports multiple file formats and provides AI-powered insights for job seekers and recruiters.

    ### 📄 Supported Formats:
    - **Documents**: PDF, DOCX, LaTeX
    - **Images**: JPEG, PNG (with OCR)
    - **Presentations**: PowerPoint (PPTX)
    - **Spreadsheets**: Excel (XLSX)
    - **Audio**: MP3, WAV (with speech-to-text)
    - **Video**: MP4, AVI (with transcription and frame analysis)

    ### 🚀 Key Features:
    - **Multi-AI Integration**: OpenAI, Anthropic, Hugging Face
    - **Advanced OCR**: Tesseract with image enhancement
    - **Speech-to-Text**: OpenAI Whisper transcription
    - **Video Analysis**: Frame extraction with OCR
    - **ATS Scoring**: Comprehensive compatibility analysis
    - **Batch Processing**: Enterprise bulk document processing
    - **Rate Limiting**: Tier-based usage limits
    - **Real-time Analysis**: WebSocket support for live updates

    ### 🔧 API Capabilities:
    - RESTful API with comprehensive endpoints
    - Multi-format file upload and processing
    - Real-time analysis status tracking
    - Detailed format-specific insights
    - Batch processing for enterprise users
    - Analytics and reporting dashboards

    ### 🛡️ Security & Performance:
    - JWT-based authentication
    - Rate limiting and abuse prevention
    - Secure file handling and processing
    - Scalable containerized deployment
    - Comprehensive error handling

    ---
    **Version**: 2.0.0 | **License**: MIT | **Support**: [GitHub Issues](https://github.com/ZeX-ATS-AI/issues)
    """,
    version="2.0.0",
    contact={
        "name": "ZeX-ATS-AI Support",
        "url": "https://github.com/ZeX-ATS-AI",
        "email": "support@zex-ats-ai.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_url="/api/openapi.json",
    docs_url=None,  # Custom docs
    redoc_url=None,  # Custom redoc
    lifespan=lifespan,
    swagger_ui_parameters={
        "syntaxHighlight.theme": "arta",
        "tryItOutEnabled": True,
        "displayRequestDuration": True,
        "docExpansion": "list",
        "filter": True,
        "showCommonExtensions": True,
        "showExtensions": True
    }
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-Analysis-ID"]
)

# Trusted Host Middleware
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )


# Custom middleware for request timing and analysis tracking
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time and analysis tracking."""
    start_time = time.time()
    
    # Generate unique request ID
    request_id = f"req_{int(start_time * 1000000)}"
    
    # Add request context
    request.state.request_id = request_id
    request.state.start_time = start_time
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Add headers
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    response.headers["X-Request-ID"] = request_id
    
    # Log for monitoring
    if process_time > 5.0:  # Log slow requests
        logger.warning(f"Slow request: {request.method} {request.url} took {process_time:.2f}s")
    
    return response


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with detailed error responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=f"HTTP_{exc.status_code}",
            message=exc.detail,
            details={
                "path": str(request.url),
                "method": request.method,
                "request_id": getattr(request.state, 'request_id', None)
            }
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_code="INTERNAL_SERVER_ERROR",
            message="An internal server error occurred",
            details={
                "path": str(request.url),
                "method": request.method,
                "request_id": getattr(request.state, 'request_id', None)
            } if settings.DEBUG else None
        ).dict()
    )


# Include routers
app.include_router(
    analyze.router,
    prefix="/api/v1/analyze",
    tags=["Analysis - Multi-Format Support"],
    responses={
        400: {"description": "Bad Request", "model": ErrorResponse},
        401: {"description": "Unauthorized", "model": ErrorResponse},
        403: {"description": "Forbidden", "model": ErrorResponse},
        413: {"description": "File Too Large", "model": ErrorResponse},
        422: {"description": "Unprocessable Entity", "model": ErrorResponse},
        429: {"description": "Rate Limit Exceeded", "model": ErrorResponse},
        500: {"description": "Internal Server Error", "model": ErrorResponse}
    }
)


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "ZeX-ATS-AI Enhanced Multi-Format Platform",
        "version": "2.0.0",
        "timestamp": time.time()
    }


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check with component status."""
    try:
        health_checker = app.state.health_checker
        health_status = await health_checker.check_all_components()
        
        return {
            "status": "healthy" if health_status["overall_healthy"] else "unhealthy",
            "service": "ZeX-ATS-AI Enhanced Multi-Format Platform",
            "version": "2.0.0",
            "timestamp": time.time(),
            "components": health_status["components"],
            "supported_formats": {
                "total": 16,
                "documents": ["PDF", "DOCX", "LaTeX"],
                "images": ["JPEG", "PNG"],
                "presentations": ["PPTX"],
                "spreadsheets": ["XLSX"],
                "audio": ["MP3", "WAV"],
                "video": ["MP4", "AVI"]
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": "Health check failed",
                "timestamp": time.time()
            }
        )


@app.get("/info", tags=["Information"])
async def get_platform_info():
    """Get platform information and capabilities."""
    return {
        "platform": "ZeX-ATS-AI Enhanced Multi-Format Platform",
        "version": "2.0.0",
        "description": "Advanced ATS Resume Analyzer with comprehensive document processing",
        "capabilities": {
            "supported_formats": {
                "documents": {
                    "pdf": "Advanced PDF parsing with text and image extraction",
                    "docx": "Microsoft Word document structure analysis",
                    "tex": "LaTeX command parsing and text cleaning"
                },
                "images": {
                    "jpg": "JPEG images with OCR extraction",
                    "png": "PNG images with OCR extraction"
                },
                "presentations": {
                    "pptx": "PowerPoint slide content extraction"
                },
                "spreadsheets": {
                    "xlsx": "Excel worksheet data analysis"
                },
                "audio": {
                    "mp3": "MP3 audio with speech-to-text transcription",
                    "wav": "WAV audio with speech-to-text transcription"
                },
                "video": {
                    "mp4": "MP4 video with audio transcription and frame OCR",
                    "avi": "AVI video with audio transcription and frame OCR"
                }
            },
            "ai_models": [
                "OpenAI GPT-4/GPT-3.5",
                "Anthropic Claude",
                "Hugging Face Transformers",
                "OpenAI Whisper (Speech-to-Text)",
                "Tesseract OCR"
            ],
            "features": [
                "Multi-format document processing",
                "AI-powered content analysis",
                "ATS compatibility scoring",
                "OCR with image enhancement",
                "Speech-to-text transcription",
                "Video frame analysis",
                "Batch processing (Enterprise)",
                "Real-time analysis tracking",
                "Comprehensive error handling"
            ]
        },
        "subscription_tiers": {
            "free": {
                "max_file_size": "10MB",
                "formats": ["PDF", "DOCX", "TXT"],
                "analyses_per_month": 50
            },
            "pro": {
                "max_file_size": "25MB", 
                "formats": "All supported formats",
                "analyses_per_month": 500,
                "advanced_ai": True
            },
            "enterprise": {
                "max_file_size": "50MB",
                "formats": "All supported formats",
                "analyses_per_month": "Unlimited",
                "batch_processing": True,
                "api_access": True,
                "priority_support": True
            }
        },
        "api_documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_schema": "/api/openapi.json"
        }
    }


# Custom documentation endpoints
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with enhanced styling."""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Interactive API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Custom ReDoc documentation."""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - API Reference",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )


# Custom OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema with enhanced metadata."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="ZeX-ATS-AI Enhanced Multi-Format Platform",
        version="2.0.0",
        description=app.description,
        routes=app.routes,
        tags=[
            {
                "name": "Analysis - Multi-Format Support",
                "description": "Advanced multi-format document analysis endpoints supporting PDF, DOCX, LaTeX, images, audio, video, and more."
            },
            {
                "name": "Health",
                "description": "System health monitoring and status endpoints."
            },
            {
                "name": "Information",
                "description": "Platform information and capabilities."
            }
        ]
    )
    
    # Add custom schema extensions
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    openapi_schema["servers"] = [
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://api.zex-ats-ai.com", "description": "Production server"}
    ]
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        },
        "APIKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Static files for development
if settings.DEBUG:
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint with platform overview."""
    return {
        "message": "Welcome to ZeX-ATS-AI Enhanced Multi-Format Platform! 🚀",
        "description": "Advanced ATS Resume Analyzer with comprehensive document processing capabilities",
        "version": "2.0.0",
        "supported_formats": [
            "PDF", "DOCX", "LaTeX", "JPEG", "PNG", 
            "PPTX", "XLSX", "MP3", "WAV", "MP4", "AVI"
        ],
        "documentation": {
            "interactive_docs": "/docs",
            "api_reference": "/redoc",
            "platform_info": "/info",
            "health_status": "/health"
        },
        "quick_start": {
            "1": "Upload your resume in any supported format",
            "2": "Get comprehensive ATS analysis with AI insights",
            "3": "Receive actionable recommendations for improvement",
            "4": "Track your progress with detailed analytics"
        }
    }


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
        use_colors=True,
        reload_includes=["*.py"],
        reload_excludes=["tests/*", "*.pyc", "__pycache__"]
    )
