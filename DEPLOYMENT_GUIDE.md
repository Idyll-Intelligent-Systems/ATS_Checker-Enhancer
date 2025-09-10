# 🚀 ZeX-ATS-AI Universal Deployment Guide

**One-Click Deployment for Any Platform**

This repository includes universal deployment scripts that automatically detect your platform and deploy ZeX-ATS-AI accordingly. Whether you're on Mac, Windows, Linux, Android, iOS, or want to deploy to web platforms - we've got you covered!

---

## 🎯 Quick Start (Any Platform)

### **Option 1: Universal Python Script (Recommended)**
```bash
# Clone the repository
git clone https://github.com/Idyll-Intelligent-Systems/ATS_Checker-Enhancer.git
cd ATS_Checker-Enhancer

# Run universal deployment script
python3 universal_deploy.py
```

This single script will:
- ✅ **Auto-detect your platform** (Mac/Windows/Linux/Android/iOS/Web)
- ✅ **Install dependencies** automatically
- ✅ **Configure the environment** for your platform
- ✅ **Test the deployment** with comprehensive validation
- ✅ **Start the service** with optimized settings

---

## 🖥️ Desktop Platforms

### **macOS**
```bash
# Using the universal script (auto-detects macOS)
python3 universal_deploy.py

# Manual macOS deployment
./setup-dev.sh
docker-compose up -d
python3 main.py
```
**Features**: Full feature set, Docker support, background services

### **Windows**
```bash
# Using the universal script (auto-detects Windows)
python universal_deploy.py

# Or double-click: universal_deploy.py
# Or run start_zex_ats.bat (after deployment)
```
**Features**: Full feature set, Docker Desktop support, Windows services

### **Linux**
```bash
# Using the universal script (auto-detects Linux)
python3 universal_deploy.py

# Manual Linux deployment  
sudo ./setup-dev.sh
docker-compose up -d
python3 main.py
```
**Features**: Full feature set, Docker support, systemd services

---

## 📱 Mobile Platforms

### **Android (Termux)**
```bash
# Install Termux from F-Droid or Google Play
# Open Termux and run:
pkg install git python
git clone https://github.com/Idyll-Intelligent-Systems/ATS_Checker-Enhancer.git
cd ATS_Checker-Enhancer

# Use mobile deployment script
./deploy_mobile.sh

# Or use universal script (auto-detects Android)
python3 universal_deploy.py
```
**Features**: Mobile-optimized UI, reduced formats (PDF, DOCX, TXT, JPG, PNG), 8080 port

### **iOS (iSH App)**
```bash
# Install iSH from App Store
# Open iSH and run:
apk add git python3
git clone https://github.com/Idyll-Intelligent-Systems/ATS_Checker-Enhancer.git
cd ATS_Checker-Enhancer

# Use mobile deployment script
./deploy_mobile.sh

# Or use universal script (auto-detects iOS)
python3 universal_deploy.py
```
**Features**: iOS-optimized processing, essential formats only

---

## 🌐 Web Platforms

### **Vercel (Recommended for Serverless)**
```bash
# One-click deployment
```
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Idyll-Intelligent-Systems/ATS_Checker-Enhancer)

```bash
# Or manual deployment
python3 deploy_web.py
npm install -g vercel
vercel --prod
```

### **Netlify**
```bash
# One-click deployment
```
[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/Idyll-Intelligent-Systems/ATS_Checker-Enhancer)

### **Heroku**
```bash
# One-click deployment
```
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Idyll-Intelligent-Systems/ATS_Checker-Enhancer)

### **Railway**
```bash
# One-click deployment
```
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/Idyll-Intelligent-Systems/ATS_Checker-Enhancer)

### **Render**
```bash
# One-click deployment
```
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Idyll-Intelligent-Systems/ATS_Checker-Enhancer)

---

## 📋 Deployment Scripts Overview

| Script | Platform | Description |
|--------|----------|-------------|
| `universal_deploy.py` | **All Platforms** | 🎯 **Main deployment script** - Auto-detects platform and deploys accordingly |
| `deploy_mobile.sh` | Android/iOS | 📱 Mobile-optimized deployment for Termux/iSH |
| `deploy_web.py` | Web Platforms | 🌐 Creates configs for Vercel, Netlify, Heroku, etc. |
| `setup-dev.sh` | Mac/Linux | 🛠️ Development environment setup |
| `setup.sh` | Linux | 🐧 Linux-specific production setup |
| `deploy.sh` | Linux/Docker | 🐳 Docker-based deployment |

---

## 🎛️ Platform-Specific Features

### **Desktop (Mac/Windows/Linux)**
- ✅ **All 16 file formats** supported
- ✅ **Full AI processing** (OpenAI, Anthropic, Hugging Face)
- ✅ **Advanced features** (OCR, speech-to-text, video analysis)
- ✅ **Docker deployment** available
- ✅ **Background services** and job queues
- ✅ **Enterprise features** (batch processing)
- 🌐 **Port**: 8000

### **Mobile (Android/iOS)**
- ✅ **Essential formats** (PDF, DOCX, TXT, JPG, PNG)
- ✅ **Mobile-optimized UI** with touch interface
- ✅ **Reduced processing** for battery efficiency
- ✅ **Offline capabilities** where possible
- ✅ **Termux widget** (Android) for quick access
- 🌐 **Port**: 8080

### **Web Platforms**
- ✅ **Serverless optimized** processing
- ✅ **Static file serving** for UI
- ✅ **CDN integration** for global access
- ✅ **Auto-scaling** based on demand
- ✅ **SSL certificates** included
- 🌐 **Port**: Platform-specific

---

## 🔧 Configuration Options

The universal deployment script automatically configures:

### **Environment Variables**
- `ENVIRONMENT`: production/mobile/web
- `DEBUG`: true/false based on platform
- `HOST`: 0.0.0.0 (all platforms)
- `PORT`: Platform-optimized (8000/8080/auto)
- `DATABASE_URL`: SQLite for mobile/web, PostgreSQL for desktop
- `MAX_FILE_SIZE`: 50MB desktop, 10MB mobile
- `SUPPORTED_FORMATS`: All formats or mobile-optimized subset

### **Base URL Configuration**

`BASE_URL` defines the root path served by the dashboard frontend. Deployment scripts like `deploy.sh` or `deploy_web.py` replace a `__BASE_URL__` placeholder in `dashboard/index.html` with this value before publishing.

**Sample values**

- Local: `BASE_URL=http://localhost:8000`
- Staging: `BASE_URL=https://staging.example.com`
- Production: `BASE_URL=https://example.com`

**Deployment**

```bash
export BASE_URL=https://staging.example.com
./deploy.sh  # script injects BASE_URL into dashboard/index.html
```

### **Platform Optimizations**
- **Desktop**: Full feature set with Docker orchestration
- **Mobile**: Battery-efficient processing with reduced features
- **Web**: Serverless functions with static file serving

---

## 🧪 Testing Your Deployment

After deployment, the universal script runs comprehensive tests:

```bash
# Test all supported formats
python3 test_multi_format.py

# Check system health
curl http://localhost:8000/health

# Access interactive demo
open http://localhost:8000/sandbox/

# View API documentation
open http://localhost:8000/docs
```

### **Expected Test Results**
- ✅ **16 formats tested** on desktop platforms
- ✅ **5 formats tested** on mobile platforms  
- ✅ **100% success rate** for supported formats
- ✅ **ATS scoring** working correctly
- ✅ **API endpoints** responding properly

---

## 🎯 Usage Examples

### **Desktop/Web Usage**
```bash
# Start the platform
python3 universal_deploy.py

# Upload any supported file format
curl -X POST "http://localhost:8000/api/v1/analyze/resume/multi-format" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf"

# Get supported formats
curl http://localhost:8000/api/v1/analyze/supported-formats
```

### **Mobile Usage**
```bash
# Start mobile version
./start_mobile.sh

# Access mobile UI
open http://localhost:8080

# Mobile-optimized analysis
curl -X POST "http://localhost:8080/analyze" \
  -F "file=@mobile_resume.pdf"
```

---

## 🚨 Troubleshooting

### **Common Issues**

1. **Python version too old**
   ```bash
   # Install Python 3.11+
   # macOS: brew install python@3.11
   # Ubuntu: sudo apt install python3.11
   # Windows: Download from python.org
   ```

2. **Docker not available**
   ```bash
   # The script falls back to local deployment
   # Docker is optional on most platforms
   ```

3. **Mobile deployment fails**
   ```bash
   # Ensure you're in Termux (Android) or iSH (iOS)
   # Use the mobile-specific script: ./deploy_mobile.sh
   ```

4. **File upload errors**
   ```bash
   # Check file size limits (10MB mobile, 50MB desktop)
   # Verify file format is supported
   # Check CORS settings for web deployment
   ```

### **Platform-Specific Issues**

- **macOS**: Install Xcode command line tools: `xcode-select --install`
- **Windows**: Enable WSL for better compatibility
- **Linux**: Install build essentials: `sudo apt install build-essential`
- **Android**: Use F-Droid Termux for better compatibility
- **iOS**: iSH has limited package availability

---

## 📈 Performance Expectations

| Platform | Setup Time | First Upload | Processing Speed |
|----------|-----------|--------------|------------------|
| **macOS** | 3-5 minutes | ~2 seconds | 95%+ accuracy |
| **Windows** | 3-5 minutes | ~2 seconds | 95%+ accuracy |
| **Linux** | 2-4 minutes | ~2 seconds | 95%+ accuracy |
| **Android** | 5-10 minutes | ~5 seconds | 85%+ accuracy |
| **iOS** | 5-10 minutes | ~8 seconds | 80%+ accuracy |
| **Web** | 1-2 minutes | ~3 seconds | 90%+ accuracy |

---

## 🎉 Success Indicators

After successful deployment, you should see:

```bash
🎉 ZeX-ATS-AI Deployment Complete!
📱 Platform: YOUR_PLATFORM
🌐 Service URL: http://localhost:PORT
📚 API Documentation: http://localhost:PORT/docs
🎮 Interactive Demo: http://localhost:PORT/sandbox/

✅ All tests passed!
✅ Service is running
✅ Ready for file uploads
```

---

## 💡 Next Steps

1. **Test with your resume**: Upload a sample resume to verify processing
2. **Explore the API**: Check out `/docs` for comprehensive API documentation
3. **Try different formats**: Test with PDF, DOCX, images, audio, and video
4. **Configure AI models**: Add your OpenAI/Anthropic API keys for enhanced analysis
5. **Set up monitoring**: Use the CLI tools for system management

---

## 📞 Support

- 📖 **Documentation**: See `README.md` and `ENHANCEMENT_SUMMARY.md`
- 🐛 **Issues**: [GitHub Issues](https://github.com/Idyll-Intelligent-Systems/ATS_Checker-Enhancer/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Idyll-Intelligent-Systems/ATS_Checker-Enhancer/discussions)
- 🚀 **Quick Start**: See `QUICK_START.md`

---

**🎯 ZeX-ATS-AI: The most comprehensive multi-format ATS platform that runs anywhere!**
