# 🚀 ZeX-ATS-AI Quick Start Guide - Multi-Format Testing

This guide will help you quickly test the enhanced multi-format document processing capabilities of ZeX-ATS-AI.

## 🎯 Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

## ⚡ Quick Setup

### 1. Clone and Setup
```bash
git clone https://github.com/your-repo/ATS_Checker-Enhancer.git
cd ATS_Checker-Enhancer

# Setup development environment
chmod +x setup-dev.sh
./setup-dev.sh
```

### 2. Start with Docker
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 3. Test Multi-Format Processing
```bash
# Run comprehensive format tests
python3 test_multi_format.py
```

## 📄 Testing Different Formats

### 📋 **Document Formats**
```bash
# Test PDF processing
curl -X POST "http://localhost:8000/api/v1/analyze/resume/multi-format" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_resume.pdf"

# Test DOCX processing
curl -X POST "http://localhost:8000/api/v1/analyze/resume/multi-format" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_resume.docx"
```

### 🖼️ **Image Formats (OCR)**
```bash
# Test JPEG OCR
curl -X POST "http://localhost:8000/api/v1/analyze/resume/multi-format" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume_image.jpg"

# Test PNG OCR
curl -X POST "http://localhost:8000/api/v1/analyze/resume/multi-format" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume_image.png"
```

### 🎵 **Audio Formats (Speech-to-Text)**
```bash
# Test MP3 transcription
curl -X POST "http://localhost:8000/api/v1/analyze/resume/multi-format" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume_audio.mp3"

# Test WAV transcription
curl -X POST "http://localhost:8000/api/v1/analyze/resume/multi-format" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume_audio.wav"
```

### 🎬 **Video Formats (Multi-modal)**
```bash
# Test MP4 video analysis
curl -X POST "http://localhost:8000/api/v1/analyze/resume/multi-format" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume_video.mp4"
```

## 🔍 Check Supported Formats

```bash
# Get all supported formats
curl -X GET "http://localhost:8000/api/v1/analyze/supported-formats"
```

Response will show all 16 supported formats:
```json
{
  "success": true,
  "total_formats": 16,
  "categories": {
    "documents": {
      "PDF": {
        "extensions": ["pdf"],
        "description": "Portable Document Format - industry standard"
      },
      "Microsoft Word": {
        "extensions": ["docx", "doc"],
        "description": "Microsoft Word documents"
      }
    },
    "images": {
      "JPEG": {
        "extensions": ["jpg", "jpeg"],
        "description": "JPEG images with OCR extraction"
      }
    }
  }
}
```

## 📊 Sample Multi-Format Response

When you upload any supported file, you'll get comprehensive analysis:

```json
{
  "success": true,
  "analysis_id": "analysis_123456",
  "file_info": {
    "filename": "resume.pdf",
    "format": "PDF",
    "size_mb": 2.5,
    "processing_method": "PyMuPDF with OCR fallback"
  },
  "content_extraction": {
    "text_extracted": true,
    "extraction_method": "PyMuPDF with OCR fallback",
    "confidence_score": 95.5,
    "pages_processed": 2
  },
  "analysis_results": {
    "ats_score": 87,
    "ai_insights": {
      "strengths": ["Clear structure", "Relevant keywords"],
      "suggestions": ["Add quantified achievements", "Include technical skills"]
    }
  },
  "recommendations": [
    "Consider using higher resolution for better OCR results",
    "Convert to PDF for optimal ATS compatibility"
  ]
}
```

## 🎮 Interactive Testing

### 1. **Web Interface** (Sandbox)
```bash
# Open the interactive demo
open http://localhost:8000/sandbox/
```

### 2. **API Documentation**
```bash
# Access Swagger UI
open http://localhost:8000/docs

# Access ReDoc
open http://localhost:8000/redoc
```

### 3. **CLI Testing**
```bash
# Use CLI for testing
python cli.py test-formats --all

# Test specific format
python cli.py test-formats --format pdf
```

## 🔧 Advanced Testing

### **Batch Processing** (Enterprise)
```bash
# Test batch processing (requires Enterprise tier)
curl -X POST "http://localhost:8000/api/v1/analyze/document/batch-process" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@resume1.pdf" \
  -F "files=@resume2.docx" \
  -F "files=@resume3.jpg"
```

### **Performance Testing**
```bash
# Test with large files
curl -X POST "http://localhost:8000/api/v1/analyze/resume/multi-format" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@large_presentation.pptx"
```

## 🚨 Troubleshooting

### Common Issues:

1. **File too large**
   - Max size: 50MB for multimedia, 10MB for documents
   - Compress files if needed

2. **OCR confidence low**
   - Use higher resolution images
   - Ensure clear, readable text

3. **Audio transcription failed**
   - Check audio quality
   - Ensure clear speech without background noise

4. **Format not supported**
   - Check supported formats list
   - Verify file extension and MIME type

### Debug Mode:
```bash
# Run with debug logging
DEBUG=true python3 main.py
```

## 📈 Performance Expectations

| Format | File Size | Processing Time | Accuracy |
|--------|-----------|----------------|----------|
| PDF (2 pages) | 2MB | ~2.3 seconds | 95%+ |
| DOCX | 1MB | ~1.8 seconds | 98%+ |
| JPEG (OCR) | 5MB | ~4.2 seconds | 85-95% |
| MP3 (30s) | 3MB | ~8.5 seconds | 90-98% |
| MP4 (60s) | 25MB | ~15.2 seconds | 85-95% |

## 🎉 Success Indicators

✅ **All tests pass**: 16/16 formats working  
✅ **High accuracy**: >85% for all format types  
✅ **Fast processing**: <5 seconds for most files  
✅ **Robust error handling**: Graceful failures with helpful feedback  
✅ **Comprehensive analysis**: Format-specific insights and recommendations  

---

🚀 **You're now ready to test the full multi-format capabilities of ZeX-ATS-AI!**

For more details, check the [ENHANCEMENT_SUMMARY.md](ENHANCEMENT_SUMMARY.md) file.
