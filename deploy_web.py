#!/usr/bin/env python3
"""
🌐 ZeX-ATS-AI Web Application Deployment Script
Deploy to various web platforms: Vercel, Netlify, Heroku, Railway, Render, etc.
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional

def run_command(cmd: str) -> bool:
    """Run command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {cmd}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {cmd}")
        print(f"Error: {e.stderr}")
        return False

def create_vercel_config():
    """Create Vercel deployment configuration."""
    print("🔧 Creating Vercel configuration...")
    
    vercel_config = {
        "version": 2,
        "name": "zex-ats-ai",
        "builds": [
            {
                "src": "main.py",
                "use": "@vercel/python"
            }
        ],
        "routes": [
            {
                "src": "/(.*)",
                "dest": "/main.py"
            }
        ],
        "env": {
            "ENVIRONMENT": "production",
            "DATABASE_URL": "sqlite:///./data/ats.db",
            "CORS_ORIGINS": "*",
            "MAX_FILE_SIZE": "52428800"
        }
    }
    
    with open("vercel.json", "w") as f:
        json.dump(vercel_config, f, indent=2)
    
    # Create requirements.txt for Vercel
    with open("requirements_vercel.txt", "w") as f:
        f.write("""fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
SQLAlchemy==2.0.23
aiofiles==23.2.1
Pillow==10.1.0
python-docx==1.1.0
PyPDF2==3.0.1
requests==2.31.0
python-jose==3.3.0
passlib==1.7.4
bcrypt==4.1.1
jsonschema==4.20.0
email-validator==2.1.0
httpx==0.25.2
""")

def create_netlify_config():
    """Create Netlify deployment configuration."""
    print("🔧 Creating Netlify configuration...")
    
    # netlify.toml
    netlify_config = """[build]
  command = "pip install -r requirements.txt && python build_static.py"
  publish = "dist"

[build.environment]
  PYTHON_VERSION = "3.11"
  
[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/api/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
"""
    
    with open("netlify.toml", "w") as f:
        f.write(netlify_config)
    
    # Create Netlify function
    os.makedirs(".netlify/functions", exist_ok=True)
    
    with open(".netlify/functions/api.py", "w") as f:
        f.write("""from main import app
from mangum import Mangum

handler = Mangum(app)
""")

def create_heroku_config():
    """Create Heroku deployment configuration."""
    print("🔧 Creating Heroku configuration...")
    
    # Procfile
    with open("Procfile", "w") as f:
        f.write("web: uvicorn main:app --host 0.0.0.0 --port $PORT\n")
    
    # runtime.txt
    with open("runtime.txt", "w") as f:
        f.write("python-3.11.0\n")
    
    # app.json for Heroku Button
    heroku_config = {
        "name": "ZeX-ATS-AI",
        "description": "Enhanced Multi-Format ATS Resume Analyzer",
        "repository": "https://github.com/your-repo/ATS_Checker-Enhancer",
        "keywords": ["python", "fastapi", "ai", "resume", "ats"],
        "env": {
            "ENVIRONMENT": {
                "value": "production"
            },
            "DATABASE_URL": {
                "value": "sqlite:///./data/ats.db"
            },
            "OPENAI_API_KEY": {
                "description": "OpenAI API key for AI analysis",
                "required": False
            }
        },
        "formation": {
            "web": {
                "quantity": 1,
                "size": "basic"
            }
        },
        "addons": [
            "heroku-postgresql:mini"
        ]
    }
    
    with open("app.json", "w") as f:
        json.dump(heroku_config, f, indent=2)

def create_railway_config():
    """Create Railway deployment configuration."""
    print("🔧 Creating Railway configuration...")
    
    railway_config = {
        "build": {
            "builder": "nixpacks"
        },
        "deploy": {
            "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
            "healthcheckPath": "/health"
        }
    }
    
    with open("railway.json", "w") as f:
        json.dump(railway_config, f, indent=2)

def create_render_config():
    """Create Render deployment configuration."""
    print("🔧 Creating Render configuration...")
    
    render_config = {
        "services": [
            {
                "type": "web",
                "name": "zex-ats-ai",
                "runtime": "python3",
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
                "envVars": [
                    {
                        "key": "ENVIRONMENT",
                        "value": "production"
                    },
                    {
                        "key": "DATABASE_URL",
                        "value": "sqlite:///./data/ats.db"
                    }
                ]
            }
        ]
    }
    
    with open("render.yaml", "w") as f:
        json.dump(render_config, f, indent=2)

def create_docker_web_config():
    """Create Docker configuration for web deployment."""
    print("🔧 Creating Docker web configuration...")
    
    # Multi-stage Dockerfile for web
    dockerfile_content = """# Multi-stage Docker build for web deployment
FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \\
    tesseract-ocr \\
    poppler-utils \\
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/app/.local

# Copy application code
COPY . .

# Change ownership
RUN chown -R app:app /app

# Switch to app user
USER app

# Update PATH
ENV PATH=/home/app/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    with open("Dockerfile.web", "w") as f:
        f.write(dockerfile_content)

def create_static_build_script():
    """Create script to build static files for deployment."""
    print("🔧 Creating static build script...")
    
    build_script = '''#!/usr/bin/env python3
"""
Build static files for web deployment
"""
import os
import shutil
from pathlib import Path

def build_static():
    """Build static distribution."""
    print("🏗️  Building static files...")
    
    # Create dist directory
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    # Copy static files
    static_files = [
        "sandbox/index.html",
        "sandbox/style.css", 
        "sandbox/script.js"
    ]
    
    for file_path in static_files:
        if Path(file_path).exists():
            shutil.copy2(file_path, dist_dir)
    
    # Create index.html if not exists
    index_path = dist_dir / "index.html"
    if not index_path.exists():
        create_default_index(index_path)
    
    print("✅ Static build complete")

def create_default_index(index_path):
    """Create default index.html."""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZeX-ATS-AI - Multi-Format Resume Analyzer</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; }
        .container { max-width: 800px; margin: 0 auto; text-align: center; }
        h1 { font-size: 3rem; margin-bottom: 1rem; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 40px 0; }
        .feature { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }
        .btn { background: #fff; color: #667eea; padding: 15px 30px; border: none; border-radius: 50px; font-size: 1.1rem; cursor: pointer; margin: 10px; text-decoration: none; display: inline-block; transition: transform 0.2s; }
        .btn:hover { transform: translateY(-2px); }
        .formats { background: rgba(0,0,0,0.2); padding: 20px; border-radius: 10px; margin: 30px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 ZeX-ATS-AI</h1>
        <h2>Enhanced Multi-Format Resume Analyzer</h2>
        <p>Advanced AI-powered resume analysis supporting 16+ file formats</p>
        
        <div class="formats">
            <h3>📄 Supported Formats</h3>
            <p>PDF • DOCX • LaTeX • JPEG • PNG • PPTX • XLSX • MP3 • WAV • MP4 • AVI</p>
        </div>
        
        <div class="features">
            <div class="feature">
                <h3>🤖 AI Analysis</h3>
                <p>Multi-AI integration with OpenAI, Anthropic, and Hugging Face</p>
            </div>
            <div class="feature">
                <h3>🎯 ATS Optimization</h3>
                <p>Comprehensive compatibility scoring and recommendations</p>
            </div>
            <div class="feature">
                <h3>🔍 Multi-Format</h3>
                <p>Process documents, images, audio, and video files</p>
            </div>
        </div>
        
        <div>
            <a href="/docs" class="btn">📚 API Documentation</a>
            <a href="/sandbox/" class="btn">🎮 Interactive Demo</a>
            <a href="/health" class="btn">🏥 System Health</a>
        </div>
        
        <div style="margin-top: 50px; opacity: 0.8;">
            <p>Deploy anywhere: Vercel • Netlify • Heroku • Railway • Render • Docker</p>
            <p>© 2024 ZeX-ATS-AI - Enhanced Multi-Format Platform</p>
        </div>
    </div>
</body>
</html>"""
    
    index_path.write_text(html_content)

if __name__ == "__main__":
    build_static()
'''
    
    with open("build_static.py", "w") as f:
        f.write(build_script)
    
    os.chmod("build_static.py", 0o755)

def create_deployment_instructions():
    """Create deployment instructions for different platforms."""
    print("📚 Creating deployment instructions...")
    
    instructions = """# 🌐 ZeX-ATS-AI Web Deployment Guide

This guide covers deploying ZeX-ATS-AI to various web platforms.

## 🚀 Quick Deploy Buttons

### Vercel
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-repo/ATS_Checker-Enhancer)

### Netlify
[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/your-repo/ATS_Checker-Enhancer)

### Heroku
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/your-repo/ATS_Checker-Enhancer)

### Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/your-repo/ATS_Checker-Enhancer)

### Render
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/your-repo/ATS_Checker-Enhancer)

## 📋 Manual Deployment Steps

### Vercel Deployment
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

### Netlify Deployment
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy
netlify deploy --prod --dir=dist
```

### Heroku Deployment
```bash
# Install Heroku CLI
# Create Heroku app
heroku create zex-ats-ai

# Add buildpack
heroku buildpacks:set heroku/python

# Deploy
git push heroku main
```

### Railway Deployment
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy
railway up
```

### Docker Web Deployment
```bash
# Build Docker image
docker build -f Dockerfile.web -t zex-ats-ai-web .

# Run container
docker run -p 8000:8000 zex-ats-ai-web
```

## ⚙️ Environment Variables

Set these environment variables in your deployment platform:

```env
ENVIRONMENT=production
DATABASE_URL=sqlite:///./data/ats.db
CORS_ORIGINS=*
MAX_FILE_SIZE=52428800
OPENAI_API_KEY=your_openai_key (optional)
ANTHROPIC_API_KEY=your_anthropic_key (optional)
```

## 🔧 Platform-Specific Notes

### Vercel
- Uses serverless functions
- SQLite database recommended
- File uploads limited to 50MB

### Netlify
- Static site with serverless functions
- Good for demo/frontend deployment
- Backend API through functions

### Heroku
- Full application deployment
- PostgreSQL add-on available
- Automatic SSL certificate

### Railway
- Modern deployment platform
- Built-in database options
- Automatic scaling

### Render
- Docker and native builds supported
- Built-in database options
- Automatic SSL and CDN

## 📊 Feature Availability by Platform

| Platform | File Upload | Database | Background Jobs | WebSockets |
|----------|-------------|----------|-----------------|------------|
| Vercel   | ✅ 50MB     | SQLite   | Limited         | ❌         |
| Netlify  | ✅ 10MB     | External | Limited         | ❌         |
| Heroku   | ✅ 50MB     | PostgreSQL| ✅             | ✅         |
| Railway  | ✅ 100MB    | PostgreSQL| ✅             | ✅         |
| Render   | ✅ 100MB    | PostgreSQL| ✅             | ✅         |

## 🚦 Post-Deployment

After deployment, verify:
1. ✅ Health check: `/health`
2. ✅ API docs: `/docs`
3. ✅ Interactive demo: `/sandbox/`
4. ✅ File upload: Test with sample resume

## 🔍 Troubleshooting

Common issues and solutions:

1. **File upload fails**
   - Check file size limits
   - Verify CORS settings
   - Check environment variables

2. **Database connection error**
   - Verify DATABASE_URL
   - Check database service status
   - Review connection settings

3. **AI analysis fails**
   - Check API keys are set
   - Verify network connectivity
   - Review rate limits

4. **Build fails**
   - Check Python version (3.11+)
   - Verify dependencies
   - Review build logs
"""
    
    with open("WEB_DEPLOYMENT.md", "w") as f:
        f.write(instructions)

def main():
    """Main deployment setup function."""
    print("🌐 ZeX-ATS-AI Web Deployment Setup")
    print("=" * 50)
    
    # Create deployment configurations
    create_vercel_config()
    create_netlify_config()  
    create_heroku_config()
    create_railway_config()
    create_render_config()
    create_docker_web_config()
    create_static_build_script()
    create_deployment_instructions()
    
    print("\n✅ Web deployment configurations created!")
    print("\n📋 Files created:")
    print("   - vercel.json (Vercel)")
    print("   - netlify.toml (Netlify)")
    print("   - Procfile, app.json (Heroku)")
    print("   - railway.json (Railway)")
    print("   - render.yaml (Render)")
    print("   - Dockerfile.web (Docker)")
    print("   - build_static.py (Static build)")
    print("   - WEB_DEPLOYMENT.md (Instructions)")
    
    print("\n🚀 Quick deployment options:")
    print("   1. Push to GitHub and use deploy buttons")
    print("   2. Use CLI tools for manual deployment")
    print("   3. Use Docker for container deployment")
    
    print("\n📚 See WEB_DEPLOYMENT.md for detailed instructions")

if __name__ == "__main__":
    main()
