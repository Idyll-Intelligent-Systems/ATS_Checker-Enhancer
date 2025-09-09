#!/usr/bin/env python3
"""
ZeX-ATS-AI Demo Server
Minimal FastAPI server for demonstration purposes
"""
import os
import sys
import uvicorn
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="ZeX-ATS-AI Enhanced Multi-Format Platform", 
    version="1.0.0",
    description="AI-powered ATS analysis with 16+ file format support"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
project_root = Path(__file__).parent
(project_root / "data").mkdir(exist_ok=True)
(project_root / "uploads").mkdir(exist_ok=True)
(project_root / "logs").mkdir(exist_ok=True)

@app.get("/")
async def root():
    """Root endpoint with platform information."""
    return {
        "name": "ZeX-ATS-AI Enhanced Multi-Format Platform",
        "version": "1.0.0",
        "status": "running",
        "supported_formats": [
            "PDF", "DOCX", "LaTeX", "TXT", 
            "JPG", "JPEG", "PNG", "TIFF",
            "PPTX", "PPT", "XLSX", "XLS",
            "MP3", "WAV", "M4A", "MP4", "AVI"
        ],
        "endpoints": {
            "documentation": "/docs",
            "demo": "/demo",
            "health": "/health",
            "analyze": "/api/v1/analyze"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "platform": "macOS"}

@app.get("/demo", response_class=HTMLResponse)
async def demo():
    """Interactive demo page."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ZeX-ATS-AI Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; border-radius: 5px; }
            .upload-area:hover { border-color: #007bff; }
            .formats { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            .btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 ZeX-ATS-AI Enhanced Multi-Format Platform</h1>
            <p><strong>Status:</strong> ✅ Running Successfully on macOS</p>
            
            <div class="formats">
                <h3>📄 Supported Formats (16 Types):</h3>
                <p><strong>Documents:</strong> PDF, DOCX, LaTeX, TXT</p>
                <p><strong>Images:</strong> JPG, JPEG, PNG, TIFF (with OCR)</p>
                <p><strong>Presentations:</strong> PPTX, PPT</p>
                <p><strong>Spreadsheets:</strong> XLSX, XLS</p>
                <p><strong>Audio:</strong> MP3, WAV, M4A (speech-to-text)</p>
                <p><strong>Video:</strong> MP4, AVI (transcription)</p>
            </div>
            
            <div class="upload-area">
                <h3>📁 Upload Your Resume</h3>
                <input type="file" id="fileInput" accept=".pdf,.docx,.txt,.jpg,.png,.pptx,.xlsx,.mp3,.mp4" style="margin: 10px;">
                <br>
                <button class="btn" onclick="analyzeFile()">🔍 Analyze Resume</button>
            </div>
            
            <div id="results" style="margin-top: 20px;"></div>
            
            <div style="text-align: center; margin-top: 30px;">
                <p><strong>🔗 Quick Links:</strong></p>
                <a href="/docs" style="margin: 10px; color: #007bff;">📚 API Documentation</a>
                <a href="/" style="margin: 10px; color: #007bff;">🏠 API Root</a>
                <a href="/health" style="margin: 10px; color: #007bff;">❤️ Health Check</a>
            </div>
        </div>
        
        <script>
            function analyzeFile() {
                const fileInput = document.getElementById('fileInput');
                const resultsDiv = document.getElementById('results');
                
                if (!fileInput.files[0]) {
                    alert('Please select a file first!');
                    return;
                }
                
                const file = fileInput.files[0];
                const fileName = file.name;
                const fileSize = (file.size / 1024 / 1024).toFixed(2);
                
                resultsDiv.innerHTML = `
                    <div style="background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px;">
                        <h4>✅ Analysis Complete!</h4>
                        <p><strong>File:</strong> ${fileName}</p>
                        <p><strong>Size:</strong> ${fileSize} MB</p>
                        <p><strong>Status:</strong> Successfully processed with AI-powered analysis</p>
                        <p><strong>Features Applied:</strong> Format detection, content extraction, ATS optimization recommendations</p>
                        <p><em>🎯 This is a demo interface. Full functionality available via API endpoints.</em></p>
                    </div>
                `;
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/api/v1/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    """Analyze uploaded resume file."""
    try:
        # Get file info
        file_content = await file.read()
        file_size = len(file_content) / 1024 / 1024  # MB
        
        # Basic file validation
        if file_size > 50:  # 50MB limit
            raise HTTPException(status_code=413, detail="File too large (max 50MB)")
        
        # Get file extension
        file_ext = Path(file.filename).suffix.lower() if file.filename else ""
        
        # Supported formats check
        supported_formats = ['.pdf', '.docx', '.latex', '.txt', '.jpg', '.jpeg', '.png', '.tiff', 
                           '.pptx', '.ppt', '.xlsx', '.xls', '.mp3', '.wav', '.m4a', '.mp4', '.avi']
        
        if file_ext not in supported_formats:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {file_ext}")
        
        # Mock analysis results
        analysis_result = {
            "file_info": {
                "filename": file.filename,
                "size_mb": round(file_size, 2),
                "format": file_ext.replace('.', '').upper()
            },
            "analysis": {
                "ats_score": 85,
                "readability_score": 92,
                "keyword_matches": 15,
                "format_compliance": "Excellent",
                "recommendations": [
                    "Add more relevant keywords for your target role",
                    "Include quantified achievements",
                    "Optimize section headings for ATS parsing"
                ]
            },
            "processing_status": "completed",
            "timestamp": "2025-09-09T16:25:00Z"
        }
        
        return JSONResponse(content=analysis_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting ZeX-ATS-AI Enhanced Multi-Format Platform...")
    print("📱 Platform: MacOS")
    print("🌐 Service URL: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🎮 Interactive Demo: http://localhost:8000/demo")
    print("❤️ Health Check: http://localhost:8000/health")
    print()
    
    uvicorn.run(
        "demo_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
