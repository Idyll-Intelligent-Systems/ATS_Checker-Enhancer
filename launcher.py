#!/usr/bin/env python3
"""
ZeX-ATS-AI Platform Launcher
Universal launcher that works on all platforms
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    try:
        # Import and run the main application
        import main
        # This will start the FastAPI server
        if __name__ == "__main__":
            import uvicorn
            uvicorn.run(
                "main:app", 
                host="0.0.0.0", 
                port=8000, 
                reload=True if os.getenv("DEBUG") == "true" else False
            )
    except ImportError as e:
        print(f"❌ Failed to import main application: {e}")
        print("Please ensure all dependencies are installed")
        sys.exit(1)

if __name__ == "__main__":
    main()
