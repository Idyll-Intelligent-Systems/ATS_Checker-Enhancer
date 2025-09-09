#!/usr/bin/env python3
"""
Simple ATS Service Launcher
Handles missing dependencies and runs the main ATS service
"""

import subprocess
import sys
import os

def install_missing_packages():
    """Install commonly missing packages for the ATS service"""
    missing_packages = [
        'textstat',
        'textblob',
        'wordcloud',
        'sklearn',
        'scikit-learn',
        'seaborn',
        'plotly',
        'dash',
        'gradio'
    ]
    
    for package in missing_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing missing package: {package}")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def download_nltk_data():
    """Download required NLTK data"""
    try:
        import nltk
        datasets = ['punkt', 'stopwords', 'wordnet', 'vader_lexicon', 'brown', 'omw-1.4']
        for dataset in datasets:
            try:
                nltk.download(dataset, quiet=True)
            except:
                pass
    except:
        pass

def run_simple_server():
    """Run a simple test server if main service fails"""
    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI(
        title="Zex ATS AI - Simple Mode",
        description="Simplified ATS service running on port 8000",
        version="1.0.0"
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "Zex ATS AI Service is running!",
            "status": "active",
            "mode": "simple",
            "endpoints": [
                "/health",
                "/docs",
                "/api/v1/analyze (coming soon)"
            ]
        }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "zex-ats-ai"}
    
    @app.get("/api/v1/status")
    async def status():
        return {
            "service": "zex-ats-ai",
            "version": "1.0.0",
            "status": "running",
            "features": [
                "Resume Analysis",
                "ATS Score Calculation", 
                "Keyword Matching",
                "Skills Extraction"
            ]
        }
    
    print("🚀 Starting Zex ATS AI Simple Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    print("🔧 Zex ATS AI Service Launcher")
    print("=" * 50)
    
    # Install missing packages
    print("📦 Checking and installing dependencies...")
    try:
        install_missing_packages()
        download_nltk_data()
        print("✅ Dependencies check complete!")
    except Exception as e:
        print(f"⚠️  Warning: Some dependencies could not be installed: {e}")
    
    # Try to run the main service
    print("\n🚀 Attempting to start main ATS service...")
    try:
        import main
        # If import succeeds, the service should start
    except Exception as e:
        print(f"❌ Main service failed to start: {e}")
        print("🔄 Falling back to simple server...")
        run_simple_server()
