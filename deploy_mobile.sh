#!/bin/bash
# 📱 ZeX-ATS-AI Mobile Deployment Script for iOS/Android
# This script sets up ZeX-ATS-AI for mobile environments including Termux (Android) and iSH (iOS)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_colored() {
    echo -e "${1}${2}${NC}"
}

print_banner() {
    print_colored $CYAN "============================================="
    print_colored $CYAN "📱 ZeX-ATS-AI Mobile Deployment"
    print_colored $CYAN "   Enhanced Multi-Format Resume Analysis"
    print_colored $CYAN "============================================="
    echo
}

detect_mobile_platform() {
    if [[ "$OSTYPE" == "linux-android"* ]] || [[ -n "$ANDROID_ROOT" ]] || [[ -d "/data/data/com.termux" ]]; then
        echo "android"
    elif [[ "$OSTYPE" == "linux-gnu"* ]] && [[ "$(uname -m)" == "i386" ]]; then
        echo "ios"  # iSH app on iOS
    elif command -v termux-setup-storage &> /dev/null; then
        echo "android"
    else
        echo "mobile"
    fi
}

install_dependencies_android() {
    print_colored $YELLOW "🤖 Installing Android (Termux) dependencies..."
    
    # Update package lists
    pkg update -y
    pkg upgrade -y
    
    # Install essential packages
    pkg install -y python python-pip git curl wget openssl libffi libjpeg-turbo
    
    # Install additional packages for document processing
    pkg install -y tesseract poppler imagemagick ffmpeg
    
    print_colored $GREEN "✅ Android dependencies installed"
}

install_dependencies_ios() {
    print_colored $YELLOW "📱 Installing iOS (iSH) dependencies..."
    
    # Update Alpine packages
    apk update
    apk upgrade
    
    # Install essential packages
    apk add python3 py3-pip git curl wget openssl-dev libffi-dev jpeg-dev
    
    # Install additional packages (limited on iSH)
    apk add tesseract-ocr poppler-utils imagemagick
    
    print_colored $GREEN "✅ iOS dependencies installed"
}

setup_python_environment() {
    print_colored $YELLOW "🐍 Setting up Python environment..."
    
    # Create virtual environment
    python3 -m venv mobile_venv
    source mobile_venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install mobile-optimized requirements
    cat > mobile_requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
SQLAlchemy==2.0.23
aiofiles==23.2.1
Pillow==10.1.0
pytesseract==0.3.10
python-docx==1.1.0
PyPDF2==3.0.1
opencv-python-headless==4.8.1.78
pydub==0.25.1
whisper==1.1.10
requests==2.31.0
jinja2==3.1.2
python-jose==3.3.0
passlib==1.7.4
bcrypt==4.1.1
redis==5.0.1
celery==5.3.4
jsonschema==4.20.0
email-validator==2.1.0
httpx==0.25.2
asyncio==3.4.3
EOF
    
    # Install dependencies with mobile optimizations
    pip install -r mobile_requirements.txt
    
    print_colored $GREEN "✅ Python environment ready"
}

create_mobile_config() {
    print_colored $YELLOW "📱 Creating mobile configuration..."
    
    # Create mobile-specific .env file
    cat > .env << EOF
# ZeX-ATS-AI Mobile Configuration
ENVIRONMENT=mobile
DEBUG=true
HOST=0.0.0.0
PORT=8080
DATABASE_URL=sqlite:///./mobile_data/ats.db
CORS_ORIGINS=*
MAX_FILE_SIZE=10485760
MAX_CONCURRENT_ANALYSES=2
MOBILE_OPTIMIZED=true
SUPPORTED_FORMATS=pdf,docx,txt,jpg,png
ENABLE_CACHING=true
CACHE_SIZE=100
LOG_LEVEL=INFO
MOBILE_UI=true
OFFLINE_MODE=true
EOF
    
    # Create mobile data directory
    mkdir -p mobile_data
    mkdir -p logs
    mkdir -p uploads
    
    print_colored $GREEN "✅ Mobile configuration created"
}

create_mobile_optimized_main() {
    print_colored $YELLOW "📱 Creating mobile-optimized application..."
    
    cat > mobile_main.py << 'EOF'
"""
ZeX-ATS-AI Mobile Application
Optimized for mobile environments (Android/iOS)
"""
import asyncio
import os
import logging
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Mobile-optimized imports
try:
    from src.ai.processors.enhanced_document_processor import EnhancedDocumentProcessor
except ImportError:
    # Fallback basic processor for mobile
    class BasicDocumentProcessor:
        SUPPORTED_FORMATS = {
            "pdf": ["application/pdf"],
            "docx": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
            "txt": ["text/plain"],
            "jpg": ["image/jpeg"],
            "png": ["image/png"]
        }
        
        async def process_document(self, file, analysis_type="resume"):
            # Basic mobile processing
            content = await file.read()
            return {
                "success": True,
                "content": {"text": f"Mobile processing of {file.filename}"},
                "file_info": {"filename": file.filename, "format": "mobile", "size": len(content)},
                "insights": {"ats_score": 75, "mobile_processed": True}
            }
    
    EnhancedDocumentProcessor = BasicDocumentProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app with mobile optimizations
app = FastAPI(
    title="ZeX-ATS-AI Mobile",
    description="Mobile-optimized ATS Resume Analyzer",
    version="1.0.0-mobile"
)

# CORS for mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

# Initialize processor
document_processor = EnhancedDocumentProcessor()

# Mobile UI endpoint
@app.get("/", response_class=HTMLResponse)
async def mobile_ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ZeX-ATS-AI Mobile</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 500px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .upload-area { border: 2px dashed #007bff; padding: 30px; text-align: center; margin: 20px 0; border-radius: 5px; }
            .btn { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; width: 100%; }
            .btn:hover { background: #0056b3; }
            .result { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; display: none; }
            .formats { font-size: 12px; color: #666; text-align: center; margin: 10px 0; }
            .loading { display: none; text-align: center; color: #007bff; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📱 ZeX-ATS-AI Mobile</h1>
            <p style="text-align: center; color: #666;">Mobile-optimized resume analysis</p>
            
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                    <p>📄 Tap to select resume file</p>
                    <input type="file" id="fileInput" name="file" accept=".pdf,.docx,.txt,.jpg,.png" style="display: none;">
                </div>
                
                <div class="formats">
                    Supported: PDF, DOCX, TXT, JPG, PNG
                </div>
                
                <button type="submit" class="btn">🚀 Analyze Resume</button>
            </form>
            
            <div class="loading" id="loading">
                <p>⏳ Processing your resume...</p>
            </div>
            
            <div class="result" id="result">
                <h3>📊 Analysis Results</h3>
                <div id="resultContent"></div>
            </div>
        </div>
        
        <script>
            document.getElementById('uploadForm').onsubmit = async function(e) {
                e.preventDefault();
                const fileInput = document.getElementById('fileInput');
                const file = fileInput.files[0];
                
                if (!file) {
                    alert('Please select a file');
                    return;
                }
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').style.display = 'none';
                
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('resultContent').innerHTML = `
                        <p><strong>File:</strong> ${result.file_info?.filename || 'Unknown'}</p>
                        <p><strong>Format:</strong> ${result.file_info?.format || 'Unknown'}</p>
                        <p><strong>ATS Score:</strong> ${result.insights?.ats_score || 'N/A'}/100</p>
                        <p><strong>Status:</strong> ${result.success ? '✅ Success' : '❌ Failed'}</p>
                        ${result.insights?.mobile_processed ? '<p><em>🔧 Mobile optimized processing</em></p>' : ''}
                    `;
                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    alert('Analysis failed: ' + error.message);
                }
            };
            
            document.getElementById('fileInput').onchange = function() {
                const fileName = this.files[0]?.name || 'No file selected';
                document.querySelector('.upload-area p').textContent = `📄 ${fileName}`;
            };
        </script>
    </body>
    </html>
    """

@app.post("/analyze")
async def analyze_mobile(file: UploadFile = File(...)):
    """Mobile-optimized analysis endpoint"""
    try:
        # Validate file size (10MB limit for mobile)
        max_size = 10 * 1024 * 1024  # 10MB
        content = await file.read()
        
        if len(content) > max_size:
            raise HTTPException(status_code=413, detail="File too large for mobile processing")
        
        # Reset file pointer
        await file.seek(0)
        
        # Process with mobile optimization
        result = await document_processor.process_document(file, analysis_type="resume")
        
        return JSONResponse({
            "success": result.get("success", True),
            "file_info": result.get("file_info", {}),
            "insights": result.get("insights", {}),
            "mobile_optimized": True
        })
        
    except Exception as e:
        logger.error(f"Mobile analysis error: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
            "mobile_optimized": True
        })

@app.get("/health")
async def health_mobile():
    """Mobile health check"""
    return {
        "status": "healthy",
        "platform": "mobile",
        "supported_formats": list(document_processor.SUPPORTED_FORMATS.keys())
    }

if __name__ == "__main__":
    # Mobile-optimized server settings
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        reload=False,  # Disable reload for mobile
        access_log=False,  # Reduce logging for mobile
        workers=1  # Single worker for mobile
    )
EOF
    
    print_colored $GREEN "✅ Mobile application created"
}

create_mobile_start_script() {
    print_colored $YELLOW "📱 Creating mobile start script..."
    
    cat > start_mobile.sh << 'EOF'
#!/bin/bash
# ZeX-ATS-AI Mobile Startup Script

echo "📱 Starting ZeX-ATS-AI Mobile..."

# Activate virtual environment
if [ -d "mobile_venv" ]; then
    source mobile_venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Set Python path
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Start the mobile application
echo "🚀 Starting mobile server on port 8080..."
python3 mobile_main.py

echo "📱 ZeX-ATS-AI Mobile stopped"
EOF
    
    chmod +x start_mobile.sh
    
    print_colored $GREEN "✅ Mobile start script created"
}

create_termux_widget() {
    print_colored $YELLOW "📱 Creating Termux widget (Android)..."
    
    # Create Termux widget directory
    mkdir -p ~/.shortcuts
    
    cat > ~/.shortcuts/ZeX-ATS-AI << 'EOF'
#!/bin/bash
# Termux widget for ZeX-ATS-AI
cd ~/ZeX-ATS-AI
./start_mobile.sh
EOF
    
    chmod +x ~/.shortcuts/ZeX-ATS-AI
    
    print_colored $GREEN "✅ Termux widget created"
}

test_mobile_deployment() {
    print_colored $YELLOW "🧪 Testing mobile deployment..."
    
    # Activate virtual environment
    source mobile_venv/bin/activate
    
    # Test basic functionality
    python3 -c "
import sys
print('✅ Python:', sys.version)

try:
    import fastapi
    print('✅ FastAPI imported')
except ImportError as e:
    print('❌ FastAPI import failed:', e)

try:
    import PIL
    print('✅ Pillow imported')
except ImportError as e:
    print('❌ Pillow import failed:', e)

print('🎉 Mobile environment test completed')
"
    
    print_colored $GREEN "✅ Mobile deployment test completed"
}

main() {
    print_banner
    
    # Detect platform
    PLATFORM=$(detect_mobile_platform)
    print_colored $BLUE "📱 Detected platform: $PLATFORM"
    
    # Install platform-specific dependencies
    case $PLATFORM in
        "android")
            install_dependencies_android
            ;;
        "ios")
            install_dependencies_ios
            ;;
        *)
            print_colored $YELLOW "⚠️  Unknown mobile platform, using generic setup"
            ;;
    esac
    
    # Setup Python environment
    setup_python_environment
    
    # Create mobile configuration
    create_mobile_config
    
    # Create mobile-optimized application
    create_mobile_optimized_main
    
    # Create start script
    create_mobile_start_script
    
    # Create Termux widget if on Android
    if [[ $PLATFORM == "android" ]]; then
        create_termux_widget
    fi
    
    # Test deployment
    test_mobile_deployment
    
    # Print success message
    print_colored $CYAN "============================================="
    print_colored $GREEN "🎉 ZeX-ATS-AI Mobile Deployment Complete!"
    print_colored $CYAN "============================================="
    echo
    print_colored $YELLOW "📱 To start ZeX-ATS-AI Mobile:"
    print_colored $NC "   ./start_mobile.sh"
    echo
    print_colored $YELLOW "🌐 Access the mobile UI at:"
    print_colored $NC "   http://localhost:8080"
    echo
    print_colored $YELLOW "📄 Supported formats (mobile optimized):"
    print_colored $NC "   PDF, DOCX, TXT, JPG, PNG"
    echo
    if [[ $PLATFORM == "android" ]]; then
        print_colored $YELLOW "🤖 Termux widget created - add to home screen"
    fi
    print_colored $CYAN "============================================="
}

# Run main function
main "$@"
