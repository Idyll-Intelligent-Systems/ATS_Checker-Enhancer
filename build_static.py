#!/usr/bin/env python3
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
