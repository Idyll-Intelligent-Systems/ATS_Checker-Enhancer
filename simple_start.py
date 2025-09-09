#!/usr/bin/env python3
"""
Simple ZeX-ATS-AI Startup Script
Bypasses configuration issues by setting environment variables directly
"""
import os
import sys
import subprocess
from pathlib import Path

# Set up environment variables directly
os.environ["ENVIRONMENT"] = "production"
os.environ["DEBUG"] = "false" 
os.environ["HOST"] = "0.0.0.0"
os.environ["PORT"] = "8000"
os.environ["DATABASE_URL"] = "sqlite:///./data/ats.db"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["SECRET_KEY"] = "zex-ats-ai-secret-key-for-development"
os.environ["JWT_SECRET_KEY"] = "zex-ats-ai-jwt-secret-key-for-development"

# Create necessary directories
project_root = Path(__file__).parent
(project_root / "data").mkdir(exist_ok=True)
(project_root / "uploads").mkdir(exist_ok=True)
(project_root / "logs").mkdir(exist_ok=True)

print("🚀 Starting ZeX-ATS-AI Enhanced Multi-Format Platform...")
print("📱 Platform: MacOS")
print("🌐 Service URL: http://localhost:8000")
print("📚 API Documentation: http://localhost:8000/docs")
print()

try:
    # Change to project directory
    os.chdir(project_root)
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    # Start uvicorn server
    venv_uvicorn = project_root / "venv" / "bin" / "uvicorn"
    if venv_uvicorn.exists():
        cmd = [str(venv_uvicorn), "main:app", "--host", "0.0.0.0", "--port", "8000"]
        print(f"🎯 Starting server: {' '.join(cmd)}")
        subprocess.run(cmd)
    else:
        print("❌ Virtual environment uvicorn not found. Please run universal_deploy.py first.")
        sys.exit(1)
        
except KeyboardInterrupt:
    print("\n⚠️  Server stopped by user.")
except Exception as e:
    print(f"❌ Error starting server: {e}")
    sys.exit(1)
