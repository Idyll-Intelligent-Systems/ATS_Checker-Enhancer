"""
ZeX Unified Platform
Single entrypoint combining:
- Multi-format ATS Analysis API (src.api.v1.analyze router)
- Auth & User / Usage endpoints
- File & Text analysis (legacy web features)
- Dynamic Website Generator endpoints
- Health & System status
Run:  python main.py
"""

import asyncio
import logging
import time
import uuid
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import io
import shutil
import tempfile
import zipfile

from fastapi import (
    FastAPI, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks, Request
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

# Core settings & services
from src.core.config import get_settings, settings
# Remove hard import of analyze router; attempt later with graceful fallback
#from src.api.v1 import analyze
from src.database.connection import get_database_session, check_database_health
from src.database.models import User, Analysis, create_tables
from src.auth.jwt_handler import JWTHandler
from src.utils.rate_limiter import RateLimiter
from src.core.ats_analyzer import ATSAnalyzer, ResumeAnalysis
try:  # Lightweight runtime may exclude heavy doc/PDF deps
    from src.core.resume_processor import ResumeProcessor  # type: ignore
except Exception as e:  # pragma: no cover - runtime degradation path
    ResumeProcessor = None  # type: ignore
    logger.warning(f"ResumeProcessor unavailable (degraded mode): {e}")
from dynamic_website_generator import DynamicWebsiteGenerator
from src.utils.system_logger import init_system_logger, log_api_event

# Initialize structured system logger
init_system_logger()

logger = logging.getLogger("zex.unified")
logging.basicConfig(level=logging.INFO)

app_start_time = time.time()
settings = get_settings()

# Security
security = HTTPBearer()
jwt_handler = JWTHandler()
rate_limiter = RateLimiter()
ats_analyzer = ATSAnalyzer()
resume_processor = ResumeProcessor() if ResumeProcessor else None
website_generator = DynamicWebsiteGenerator()

# In‑memory store for generated portfolio sites
class GenerationStatus:
    def __init__(self, id_: str, filename: str):
        self.id = id_
        self.filename = filename
        self.status = "processing"
        self.created_at = datetime.utcnow()
        self.website_path: Optional[str] = None
        self.zip_path: Optional[str] = None
        self.error: Optional[str] = None

generations = {}

# FastAPI App
app = FastAPI(
    title="ZeX Unified Platform",
    version="3.0.0",
    description="All-in-one ATS analysis, auth, and dynamic website generation in a single service.",
    openapi_url="/api/openapi.json"
)

# Middleware for API request logging
@app.middleware("http")
async def ats_system_logging_middleware(request: Request, call_next):
    start = time.time()
    method = request.method
    path = request.url.path
    try:
        response = await call_next(request)
        latency_ms = (time.time() - start) * 1000
        log_api_event(
            log_type="INFO" if response.status_code < 400 else ("ALERT" if response.status_code < 500 else "ERROR"),
            method=method,
            api=path,
            status_code=response.status_code,
            latency_ms=latency_ms,
            error=None,
            remark="OK" if response.status_code < 400 else None,
        )
        return response
    except Exception as e:  # noqa: BLE001
        latency_ms = (time.time() - start) * 1000
        log_api_event(
            log_type="ERROR",
            method=method,
            api=path,
            status_code=500,
            latency_ms=latency_ms,
            error=str(e),
            remark=None,
        )
        raise

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static mounts (if present)
if Path("dashboard").exists():
    app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")
if Path("generated_websites").exists():
    app.mount("/sites", StaticFiles(directory="generated_websites", html=True), name="sites")
if Path("website").exists():
    app.mount("/website", StaticFiles(directory="website", html=True), name="website")

# Attempt to include existing multi-format analysis router (graceful fallback if deps missing)
try:  # noqa: WPS501
    from src.api.v1 import analyze  # type: ignore
    app.include_router(analyze.router, prefix="/api/v1/analyze", tags=["Multi-Format Analysis"])
    logger.info("Multi-format analysis router enabled")
except Exception as e:  # pragma: no cover - optional feature
    logger.warning(f"Multi-format analysis router disabled: {e}")

# ---------- Auth & User Helpers ----------
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt_handler.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        async with get_database_session() as session:
            # Works for sync or async session (SQLite fallback)
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

async def check_rate_limit(user: User = Depends(get_current_user)):
    allowed = await rate_limiter.check_limit(str(user.id), user.subscription_tier)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return user

# ---------- Auth Endpoints ----------
@app.post("/auth/register")
async def register_user(email: str = Form(...), password: str = Form(...), full_name: str = Form(...)):
    async with get_database_session() as session:
        existing = session.query(User).filter(User.email == email).first()
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")
        user = User(email=email, full_name=full_name, subscription_tier="free")
        user.set_password(password)
        session.add(user)
        session.commit()
        token = jwt_handler.create_access_token({"sub": str(user.id), "email": user.email})
        return {"access_token": token, "token_type": "bearer", "user": user.to_dict()}

@app.post("/auth/login")
async def login_user(email: str = Form(...), password: str = Form(...)):
    async with get_database_session() as session:
        user = session.query(User).filter(User.email == email).first()
        if not user or not user.check_password(password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user.last_login = datetime.utcnow()
        session.commit()
        token = jwt_handler.create_access_token({"sub": str(user.id), "email": user.email})
        return {"access_token": token, "token_type": "bearer", "user": user.to_dict()}

@app.get("/user/profile")
async def user_profile(user: User = Depends(get_current_user)):
    return user.to_dict()

@app.get("/user/usage")
async def user_usage(user: User = Depends(get_current_user)):
    usage = await rate_limiter.get_current_usage(str(user.id))
    limits = rate_limiter.get_tier_limits(user.subscription_tier)
    return {"usage": usage, "limits": limits}

# ---------- Resume Analysis (Unified) ----------
@app.post("/analyze/file")
async def analyze_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    target_role: Optional[str] = Form(None),
    user: User = Depends(check_rate_limit)
):
    start = time.time()
    analysis_id = str(uuid.uuid4())
    if resume_processor is None:
        raise HTTPException(status_code=503, detail="Document processing not available in slim runtime. Install full requirements.")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    try:
        processed = await resume_processor.process_resume_file(io.BytesIO(content), file.filename)
        analysis: ResumeAnalysis = await ats_analyzer.analyze_resume(
            processed.cleaned_text, job_description, target_role
        )
        background_tasks.add_task(_store_analysis, user.id, analysis_id, analysis, processed.metadata, file.filename)
        return {
            "analysis_id": analysis_id,
            "analysis": analysis.to_dict(),
            "file_metadata": processed.metadata.to_dict() if hasattr(processed.metadata, 'to_dict') else {},
            "processing_time": round(time.time() - start, 3)
        }
    except Exception as e:
        logger.error(f"File analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.post("/analyze/text")
async def analyze_text(
    background_tasks: BackgroundTasks,
    resume_text: str = Form(...),
    job_description: Optional[str] = Form(None),
    target_role: Optional[str] = Form(None),
    user: User = Depends(check_rate_limit)
):
    if resume_processor is None:
        raise HTTPException(status_code=503, detail="Text processing not available in slim runtime. Install full requirements.")
    if len(resume_text) < 50:
        raise HTTPException(status_code=400, detail="Resume text too short")
    start = time.time()
    analysis_id = str(uuid.uuid4())
    try:
        processed = await resume_processor.process_resume_text(resume_text)
        analysis: ResumeAnalysis = await ats_analyzer.analyze_resume(
            processed.cleaned_text, job_description, target_role
        )
        background_tasks.add_task(_store_analysis, user.id, analysis_id, analysis, processed.metadata, "text_input")
        return {
            "analysis_id": analysis_id,
            "analysis": analysis.to_dict(),
            "processing_time": round(time.time() - start, 3)
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str, user: User = Depends(get_current_user)):
    async with get_database_session() as session:
        record = session.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == user.id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return {"analysis": record.result, "created_at": record.created_at, "filename": record.filename}

@app.get("/analysis/history")
async def analysis_history(limit: int = 10, offset: int = 0, user: User = Depends(get_current_user)):
    async with get_database_session() as session:
        q = session.query(Analysis).filter(Analysis.user_id == user.id).order_by(Analysis.created_at.desc())
        items = q.offset(offset).limit(limit).all()
        return {
            "analyses": [
                {"id": str(a.id), "filename": a.filename, "created_at": a.created_at, "overall_score": a.overall_score}
                for a in items
            ],
            "total": q.count()
        }

# ---------- Dynamic Website Generation ----------
@app.post("/website/generate")
async def generate_website(
    file: UploadFile = File(...),
    theme: str = Form("modern"),
    output_name: Optional[str] = Form(None),
    user: User = Depends(get_current_user)
):
    allowed = {'.pdf', '.docx', '.doc', '.txt'}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {', '.join(allowed)}")
    gen_id = str(uuid.uuid4())
    generations[gen_id] = GenerationStatus(gen_id, file.filename)
    asyncio.create_task(_process_site(gen_id, file, theme, output_name))
    return {"generation_id": gen_id, "status": "processing"}

@app.get("/website/status/{generation_id}")
async def site_status(generation_id: str):
    status = generations.get(generation_id)
    if not status:
        raise HTTPException(status_code=404, detail="Generation ID not found")
    resp = {
        "generation_id": generation_id,
        "status": status.status,
        "filename": status.filename,
        "created_at": status.created_at
    }
    if status.status == "completed":
        resp["download_url"] = f"/website/download/{generation_id}"
        if status.website_path:
            resp["preview_url"] = f"/sites/{Path(status.website_path).name}/index.html"
    if status.error:
        resp["error"] = status.error
    return resp

@app.get("/website/download/{generation_id}")
async def site_download(generation_id: str):
    status = generations.get(generation_id)
    if not status or status.status != "completed" or not status.zip_path:
        raise HTTPException(status_code=404, detail="Not ready")
    return FileResponse(path=status.zip_path, filename=f"portfolio-{generation_id[:8]}.zip", media_type="application/zip")

# ---------- Health & Info ----------
@app.get("/health")
async def health():
    return {"status": "healthy", "uptime_seconds": int(time.time() - app_start_time), "version": app.version}

@app.get("/health/detailed")
async def health_detailed():
    db_health = await check_database_health()
    return {
        "status": "healthy" if db_health.get("status") == "healthy" else "degraded",
        "database": db_health,
        "rate_limiter": {"redis": bool(rate_limiter.redis_client)},
        "uptime_seconds": int(time.time() - app_start_time),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
async def root():
    return {
        "message": "Welcome to ZeX Unified Platform 🚀",
        "docs": "/docs",
        "api_schema": "/api/openapi.json",
        "feature_groups": ["auth", "analysis", "website_generator"],
        "analysis_endpoints": ["POST /analyze/file", "POST /analyze/text"],
        "multi_format_router": "enabled" if 'analyze' in globals() else "disabled",
        "website_generator": {"start": "POST /website/generate", "status": "GET /website/status/{id}"}
    }

# ---------- Internal Helpers ----------
async def _store_analysis(user_id, analysis_id, analysis: ResumeAnalysis, metadata, filename: str):
    try:
        async with get_database_session() as session:
            record = Analysis(
                id=analysis_id,
                user_id=user_id,
                filename=filename,
                result=analysis.to_dict(),
                metadata=metadata.to_dict() if hasattr(metadata, 'to_dict') else {},
                overall_score=analysis.ats_score.overall_score,
                keyword_score=analysis.ats_score.keyword_score,
                format_score=analysis.ats_score.format_score,
                processing_time=analysis.processing_time,
                ai_insights_included=bool(analysis.ai_insights)
            )
            session.add(record)
            # increment user counter
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.analyses_count += 1
            session.commit()
    except Exception as e:
        logger.error(f"Failed to store analysis {analysis_id}: {e}")

async def _process_site(gen_id: str, file: UploadFile, theme: str, output_name: Optional[str]):
    status: GenerationStatus = generations[gen_id]
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        if not output_name:
            output_name = f"portfolio-{gen_id[:8]}"
        resume_data = website_generator.extract_resume_data(tmp_path)
        site_path = website_generator.generate_website(resume_data, output_name, theme)
        zip_path = website_generator.create_zip_package(site_path)
        status.status = "completed"
        status.website_path = site_path
        status.zip_path = zip_path
        Path(tmp_path).unlink(missing_ok=True)
    except Exception as e:
        status.status = "error"
        status.error = str(e)
        logger.error(f"Website generation failed {gen_id}: {e}")

# ---------- Startup / Shutdown ----------
@app.on_event("startup")
async def startup():
    logger.info("Starting ZeX Unified Platform ...")
    await create_tables()
    await rate_limiter.initialize()
    logger.info("Startup complete")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down ZeX Unified Platform")

# ---------- Run ----------
if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)
