"""
Web API for Dynamic Website Generator
FastAPI-based web service for generating portfolio websites from resume uploads
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, List
import uuid
import json
import asyncio
from datetime import datetime, timedelta

from dynamic_website_generator import DynamicWebsiteGenerator

app = FastAPI(
    title="Dynamic Website Generator API",
    description="Generate personalized portfolio websites from resume uploads",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="generated_websites"), name="static")

# Global generator instance
generator = DynamicWebsiteGenerator()

# Store for tracking generations (in production, use a database)
generations = {}

class GenerationStatus:
    def __init__(self, id: str, filename: str):
        self.id = id
        self.filename = filename
        self.status = "processing"
        self.created_at = datetime.now()
        self.website_path = None
        self.zip_path = None
        self.error = None

@app.get("/")
async def root():
    """API health check and information"""
    return {
        "message": "Dynamic Website Generator API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "upload": "/generate",
            "status": "/status/{generation_id}",
            "download": "/download/{generation_id}",
            "preview": "/preview/{generation_id}",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/generate")
async def generate_website(
    file: UploadFile = File(...),
    theme: str = Form("modern"),
    output_name: Optional[str] = Form(None)
):
    """Generate a website from uploaded resume"""
    
    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.doc', '.txt'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique ID
    generation_id = str(uuid.uuid4())
    
    # Create generation status
    status = GenerationStatus(generation_id, file.filename)
    generations[generation_id] = status
    
    # Process asynchronously
    asyncio.create_task(process_resume(generation_id, file, theme, output_name))
    
    return {
        "generation_id": generation_id,
        "status": "processing",
        "message": "Resume processing started. Use the generation_id to check status."
    }

async def process_resume(
    generation_id: str,
    file: UploadFile,
    theme: str,
    output_name: Optional[str]
):
    """Process resume file asynchronously"""
    status = generations[generation_id]
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Generate output name if not provided
        if not output_name:
            output_name = f"portfolio-{generation_id[:8]}"
        
        # Extract resume data
        resume_data = generator.extract_resume_data(temp_file_path)
        
        # Generate website
        website_path = generator.generate_website(resume_data, output_name, theme)
        
        # Create zip package
        zip_path = generator.create_zip_package(website_path)
        
        # Update status
        status.status = "completed"
        status.website_path = website_path
        status.zip_path = zip_path
        
        # Clean up temp file
        Path(temp_file_path).unlink()
        
    except Exception as e:
        status.status = "error"
        status.error = str(e)

@app.get("/status/{generation_id}")
async def get_status(generation_id: str):
    """Get generation status"""
    if generation_id not in generations:
        raise HTTPException(status_code=404, detail="Generation ID not found")
    
    status = generations[generation_id]
    
    response = {
        "generation_id": generation_id,
        "status": status.status,
        "filename": status.filename,
        "created_at": status.created_at.isoformat()
    }
    
    if status.status == "error":
        response["error"] = status.error
    elif status.status == "completed":
        response["download_url"] = f"/download/{generation_id}"
        response["preview_url"] = f"/preview/{generation_id}"
    
    return response

@app.get("/download/{generation_id}")
async def download_website(generation_id: str):
    """Download generated website as zip"""
    if generation_id not in generations:
        raise HTTPException(status_code=404, detail="Generation ID not found")
    
    status = generations[generation_id]
    
    if status.status != "completed":
        raise HTTPException(status_code=400, detail="Website not ready for download")
    
    if not status.zip_path or not Path(status.zip_path).exists():
        raise HTTPException(status_code=404, detail="Zip file not found")
    
    return FileResponse(
        path=status.zip_path,
        filename=f"portfolio-{generation_id[:8]}.zip",
        media_type="application/zip"
    )

@app.get("/preview/{generation_id}")
async def preview_website(generation_id: str):
    """Get preview information for generated website"""
    if generation_id not in generations:
        raise HTTPException(status_code=404, detail="Generation ID not found")
    
    status = generations[generation_id]
    
    if status.status != "completed":
        raise HTTPException(status_code=400, detail="Website not ready for preview")
    
    if not status.website_path or not Path(status.website_path).exists():
        raise HTTPException(status_code=404, detail="Website files not found")
    
    # Read profile data for preview
    profile_path = Path(status.website_path) / "data" / "profile.json"
    if profile_path.exists():
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile_data = json.load(f)
    else:
        profile_data = {}
    
    return {
        "generation_id": generation_id,
        "preview_url": f"/static/{Path(status.website_path).name}/index.html",
        "profile_data": profile_data,
        "files": list(Path(status.website_path).rglob("*"))[:20]  # Limit file list
    }

@app.get("/themes")
async def get_available_themes():
    """Get list of available themes"""
    return {
        "themes": [
            {
                "id": "modern",
                "name": "Modern",
                "description": "Clean, contemporary design with blue accents",
                "preview": "/static/theme-previews/modern.jpg"
            },
            {
                "id": "professional",
                "name": "Professional",
                "description": "Conservative, business-focused layout",
                "preview": "/static/theme-previews/professional.jpg"
            },
            {
                "id": "creative",
                "name": "Creative",
                "description": "Artistic, colorful design for creative professionals",
                "preview": "/static/theme-previews/creative.jpg"
            },
            {
                "id": "minimal",
                "name": "Minimal",
                "description": "Simple, clean layout with minimal styling",
                "preview": "/static/theme-previews/minimal.jpg"
            }
        ]
    }

@app.delete("/cleanup/{generation_id}")
async def cleanup_generation(generation_id: str):
    """Clean up generation files (admin endpoint)"""
    if generation_id not in generations:
        raise HTTPException(status_code=404, detail="Generation ID not found")
    
    status = generations[generation_id]
    
    # Remove files
    if status.website_path and Path(status.website_path).exists():
        shutil.rmtree(status.website_path)
    
    if status.zip_path and Path(status.zip_path).exists():
        Path(status.zip_path).unlink()
    
    # Remove from tracking
    del generations[generation_id]
    
    return {"message": "Generation cleaned up successfully"}

@app.get("/admin/generations")
async def list_generations():
    """List all generations (admin endpoint)"""
    return {
        "total": len(generations),
        "generations": [
            {
                "id": gen_id,
                "status": status.status,
                "filename": status.filename,
                "created_at": status.created_at.isoformat(),
                "age_hours": (datetime.now() - status.created_at).total_seconds() / 3600
            }
            for gen_id, status in generations.items()
        ]
    }

@app.post("/admin/cleanup-old")
async def cleanup_old_generations(max_age_hours: int = 24):
    """Clean up old generations (admin endpoint)"""
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    
    cleaned = []
    for gen_id, status in list(generations.items()):
        if status.created_at < cutoff_time:
            try:
                await cleanup_generation(gen_id)
                cleaned.append(gen_id)
            except:
                pass
    
    return {
        "message": f"Cleaned up {len(cleaned)} old generations",
        "cleaned_ids": cleaned
    }

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    
    # Create necessary directories
    Path("generated_websites").mkdir(exist_ok=True)
    
    print("🚀 Starting Dynamic Website Generator API")
    print("📝 Upload resumes at: http://localhost:8080/docs")
    print("🔧 API documentation: http://localhost:8080/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8080)
