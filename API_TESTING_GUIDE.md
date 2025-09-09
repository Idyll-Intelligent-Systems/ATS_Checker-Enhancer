# ZeX Platform v3.0.0 - Comprehensive API Testing Guide

## Overview

This guide provides comprehensive curl commands and sample data for testing all ZeX Platform services. The platform includes advanced ATS analysis, dynamic website generation, file processing, system monitoring, and real-time analytics.

## Base Configuration

```bash
# Set your base URL (adjust port as needed)
export ZEX_BASE_URL="http://localhost:4000"

# Alternative for production
# export ZEX_BASE_URL="https://your-production-domain.com"
```

## 1. Health & System Monitoring

### 1.1 Basic Health Check
```bash
curl -X GET "${ZEX_BASE_URL}/health" \
  -H "Content-Type: application/json" \
  | jq '.'
```

Expected Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "api": "online",
    "database": "connected",
    "spacy_nlp": "loaded",
    "file_processor": "ready"
  },
  "version": "3.0.0"
}
```

### 1.2 Detailed System Status
```bash
curl -X GET "${ZEX_BASE_URL}/api/v1/system/status" \
  -H "Content-Type: application/json" \
  | jq '.'
```

### 1.3 Service Metrics
```bash
curl -X GET "${ZEX_BASE_URL}/api/v1/metrics" \
  -H "Content-Type: application/json" \
  | jq '.'
```

## 2. ATS Resume Analysis (Enhanced with spaCy NLP)

### 2.1 Basic ATS Analysis
```bash
curl -X POST "${ZEX_BASE_URL}/api/v1/analyze" \
  -F "file=@sample_resume.pdf" \
  -F "job_description=We are looking for a Senior Python Developer with experience in FastAPI, Docker, AWS, and machine learning. The candidate should have strong skills in data analysis, API development, and cloud deployment." \
  -F "keywords=Python,FastAPI,Docker,AWS,Machine Learning,API,Cloud" \
  -F "company=TechCorp Inc" \
  | jq '.'
```

### 2.2 Advanced ATS Analysis with Custom Parameters
```bash
curl -X POST "${ZEX_BASE_URL}/api/v1/analyze" \
  -F "file=@resume_sample.pdf" \
  -F "job_description=Looking for a Full-Stack Developer proficient in React, Node.js, PostgreSQL, and DevOps practices. Experience with microservices, containerization, and CI/CD pipelines preferred." \
  -F "keywords=React,Node.js,PostgreSQL,DevOps,Microservices,Docker,Kubernetes,CI/CD" \
  -F "company=InnovateTech Solutions" \
  -F "analysis_depth=comprehensive" \
  -F "include_suggestions=true" \
  -F "skill_matching_threshold=0.7" \
  | jq '.'
```

### 2.3 Bulk Resume Analysis
```bash
curl -X POST "${ZEX_BASE_URL}/api/v1/analyze/batch" \
  -F "files[]=@resume1.pdf" \
  -F "files[]=@resume2.pdf" \
  -F "files[]=@resume3.docx" \
  -F "job_description=Senior Software Engineer position requiring expertise in cloud technologies, microservices, and agile development." \
  -F "keywords=Cloud,Microservices,Agile,Java,Spring,AWS,Docker" \
  | jq '.'
```

### 2.4 Get Analysis Results by Job ID
```bash
# First, get the job_id from the initial analysis response
JOB_ID="your_job_id_here"

curl -X GET "${ZEX_BASE_URL}/api/v1/analyze/${JOB_ID}" \
  -H "Content-Type: application/json" \
  | jq '.'
```

### Sample Resume Content for Testing
Create a sample resume file `sample_resume.txt`:
```text
John Doe
Senior Software Engineer
Email: john.doe@email.com
Phone: (555) 123-4567

EXPERIENCE:
- 5+ years of Python development using Django and FastAPI
- Extensive experience with AWS services including EC2, S3, Lambda
- Proficient in Docker containerization and Kubernetes orchestration
- Strong background in machine learning using scikit-learn and TensorFlow
- Experience with PostgreSQL, MongoDB, and Redis databases
- Skilled in API development, microservices architecture, and DevOps practices

SKILLS:
Python, FastAPI, Django, AWS, Docker, Kubernetes, Machine Learning, PostgreSQL, API Development, Cloud Computing, DevOps, CI/CD, Git, Linux

EDUCATION:
Bachelor's Degree in Computer Science
Master's Degree in Machine Learning

CERTIFICATIONS:
- AWS Solutions Architect Associate
- Docker Certified Associate
```

## 3. Dynamic Website Generation

### 3.1 Generate Website from Resume
```bash
curl -X POST "${ZEX_BASE_URL}/api/v1/generate-website" \
  -F "file=@sample_resume.pdf" \
  -F "template=modern" \
  -F "theme=professional" \
  -F "include_projects=true" \
  -F "include_skills=true" \
  -F "color_scheme=blue" \
  | jq '.'
```

### 3.2 Generate with Advanced Customization
```bash
curl -X POST "${ZEX_BASE_URL}/api/v1/generate-website" \
  -F "file=@portfolio_data.json" \
  -F "template=creative" \
  -F "theme=dark" \
  -F "include_projects=true" \
  -F "include_skills=true" \
  -F "include_contact=true" \
  -F "animation_style=fade" \
  -F "layout=grid" \
  -F "color_scheme=purple" \
  -F "font_family=Inter" \
  | jq '.'
```

### 3.3 List Available Templates
```bash
curl -X GET "${ZEX_BASE_URL}/api/v1/templates" \
  -H "Content-Type: application/json" \
  | jq '.'
```

### 3.4 Preview Website Generation
```bash
curl -X POST "${ZEX_BASE_URL}/api/v1/generate-website/preview" \
  -F "file=@resume.pdf" \
  -F "template=minimal" \
  -F "theme=elegant" \
  | jq '.'
```

### Sample Portfolio JSON for Testing
Create `portfolio_data.json`:
```json
{
  "personal_info": {
    "name": "Jane Smith",
    "title": "Full-Stack Developer",
    "email": "jane.smith@email.com",
    "phone": "(555) 987-6543",
    "location": "San Francisco, CA",
    "website": "https://janesmith.dev",
    "linkedin": "https://linkedin.com/in/janesmith",
    "github": "https://github.com/janesmith"
  },
  "summary": "Passionate full-stack developer with 7+ years of experience building scalable web applications using modern technologies.",
  "skills": {
    "frontend": ["React", "Vue.js", "TypeScript", "Tailwind CSS"],
    "backend": ["Node.js", "Python", "Express", "FastAPI"],
    "database": ["PostgreSQL", "MongoDB", "Redis"],
    "tools": ["Docker", "AWS", "Git", "Jest"]
  },
  "projects": [
    {
      "name": "E-commerce Platform",
      "description": "Built a full-stack e-commerce platform using React and Node.js",
      "technologies": ["React", "Node.js", "PostgreSQL", "Stripe"],
      "url": "https://github.com/janesmith/ecommerce"
    },
    {
      "name": "Task Management App",
      "description": "Real-time collaborative task management application",
      "technologies": ["Vue.js", "Socket.io", "MongoDB", "Express"],
      "url": "https://github.com/janesmith/taskapp"
    }
  ],
  "experience": [
    {
      "company": "TechStart Inc",
      "position": "Senior Full-Stack Developer",
      "duration": "2021 - Present",
      "description": "Led development of customer-facing web applications serving 100k+ users"
    }
  ]
}
```

## 4. Multi-Format File Processing

### 4.1 Process PDF Document
```bash
curl -X POST "${ZEX_BASE_URL}/api/v1/process-file" \
  -F "file=@document.pdf" \
  -F "extract_text=true" \
  -F "extract_metadata=true" \
  -F "analyze_structure=true" \
  | jq '.'
```

### 4.2 Process Word Document
```bash
curl -X POST "${ZEX_BASE_URL}/api/v1/process-file" \
  -F "file=@document.docx" \
  -F "extract_text=true" \
  -F "extract_images=true" \
  -F "convert_format=html" \
  | jq '.'
```

### 4.3 Process Image File
```bash
curl -X POST "${ZEX_BASE_URL}/api/v1/process-file" \
  -F "file=@image.png" \
  -F "extract_text=true" \
  -F "image_analysis=true" \
  -F "ocr_enabled=true" \
  | jq '.'
```

### 4.4 Get Processing Status
```bash
PROCESS_ID="your_process_id_here"

curl -X GET "${ZEX_BASE_URL}/api/v1/process-file/${PROCESS_ID}/status" \
  -H "Content-Type: application/json" \
  | jq '.'
```

## 5. Dashboard and Analytics

### 5.1 Get Dashboard Statistics
```bash
curl -X GET "${ZEX_BASE_URL}/api/v1/dashboard/stats" \
  -H "Content-Type: application/json" \
  | jq '.'
```

### 5.2 Get Usage Analytics
```bash
curl -X GET "${ZEX_BASE_URL}/api/v1/analytics/usage" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  | jq '.'
```

### 5.3 Get Service Performance Metrics
```bash
curl -X GET "${ZEX_BASE_URL}/api/v1/analytics/performance" \
  -H "Content-Type: application/json" \
  | jq '.'
```

### 5.4 Get Recent Activity
```bash
curl -X GET "${ZEX_BASE_URL}/api/v1/activity/recent?limit=20" \
  -H "Content-Type: application/json" \
  | jq '.'
```

## 6. File Upload and Management

### 6.1 Upload Single File
```bash
curl -X POST "${ZEX_BASE_URL}/api/v1/upload" \
  -F "file=@example.pdf" \
  -F "category=resume" \
  -F "tags=python,developer,senior" \
  | jq '.'
```

### 6.2 Upload Multiple Files
```bash
curl -X POST "${ZEX_BASE_URL}/api/v1/upload/multiple" \
  -F "files[]=@resume1.pdf" \
  -F "files[]=@resume2.docx" \
  -F "files[]=@portfolio.json" \
  -F "category=job_applications" \
  | jq '.'
```

### 6.3 List Uploaded Files
```bash
curl -X GET "${ZEX_BASE_URL}/api/v1/files?category=resume&limit=10" \
  -H "Content-Type: application/json" \
  | jq '.'
```

### 6.4 Delete File
```bash
FILE_ID="your_file_id_here"

curl -X DELETE "${ZEX_BASE_URL}/api/v1/files/${FILE_ID}" \
  -H "Content-Type: application/json" \
  | jq '.'
```

## 7. Advanced Features Testing

### 7.1 Real-time WebSocket Connection Test
```bash
# Install websocat if not available: cargo install websocat
websocat ws://localhost:4000/ws/notifications
```

### 7.2 Batch Operations
```bash
curl -X POST "${ZEX_BASE_URL}/api/v1/batch/process" \
  -H "Content-Type: application/json" \
  -d '{
    "operations": [
      {
        "type": "analyze",
        "file_path": "resume1.pdf",
        "job_description": "Python Developer position"
      },
      {
        "type": "generate_website",
        "file_path": "portfolio.json",
        "template": "modern"
      }
    ]
  }' | jq '.'
```

### 7.3 Export Analysis Results
```bash
curl -X GET "${ZEX_BASE_URL}/api/v1/export/analysis?format=csv&date_range=last_week" \
  -H "Content-Type: application/json" \
  -o analysis_results.csv
```

## 8. Error Handling Tests

### 8.1 Test Invalid File Upload
```bash
curl -X POST "${ZEX_BASE_URL}/api/v1/analyze" \
  -F "file=@invalid_file.xyz" \
  -F "job_description=Test job description" \
  | jq '.'
```

### 8.2 Test Missing Required Parameters
```bash
curl -X POST "${ZEX_BASE_URL}/api/v1/analyze" \
  -F "file=@resume.pdf" \
  | jq '.'
```

### 8.3 Test Rate Limiting
```bash
# Send multiple requests rapidly
for i in {1..20}; do
  curl -X GET "${ZEX_BASE_URL}/health" &
done
wait
```

## 9. Performance Testing

### 9.1 Large File Processing Test
```bash
# Create a large test file (if needed)
dd if=/dev/zero of=large_test.pdf bs=1M count=50

curl -X POST "${ZEX_BASE_URL}/api/v1/process-file" \
  -F "file=@large_test.pdf" \
  -H "X-Request-Timeout: 300" \
  | jq '.'
```

### 9.2 Concurrent Request Test
```bash
# Test concurrent processing
for i in {1..10}; do
  curl -X POST "${ZEX_BASE_URL}/api/v1/analyze" \
    -F "file=@resume.pdf" \
    -F "job_description=Concurrent test ${i}" &
done
wait
```

## 10. Sample Test Script

Create `test_all_apis.sh`:
```bash
#!/bin/bash

# ZeX Platform Comprehensive API Test Script
set -e

ZEX_BASE_URL="http://localhost:4000"

echo "🚀 Starting ZeX Platform API Tests..."

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s "${ZEX_BASE_URL}/health" | jq '.status'

# Test 2: System Status
echo "2. Testing System Status..."
curl -s "${ZEX_BASE_URL}/api/v1/system/status" | jq '.services'

# Test 3: ATS Analysis (create sample file if needed)
echo "3. Testing ATS Analysis..."
echo "Sample resume content" > test_resume.txt
curl -s -X POST "${ZEX_BASE_URL}/api/v1/analyze" \
  -F "file=@test_resume.txt" \
  -F "job_description=Python Developer" \
  -F "keywords=Python,AWS,Docker" | jq '.job_id'

# Test 4: Website Generation
echo "4. Testing Website Generation..."
curl -s -X POST "${ZEX_BASE_URL}/api/v1/generate-website" \
  -F "file=@test_resume.txt" \
  -F "template=modern" \
  -F "theme=professional" | jq '.status'

# Test 5: File Processing
echo "5. Testing File Processing..."
curl -s -X POST "${ZEX_BASE_URL}/api/v1/process-file" \
  -F "file=@test_resume.txt" \
  -F "extract_text=true" | jq '.status'

# Test 6: Analytics
echo "6. Testing Analytics..."
curl -s "${ZEX_BASE_URL}/api/v1/dashboard/stats" | jq '.total_analyses'

# Cleanup
rm -f test_resume.txt

echo "✅ All tests completed!"
```

Run the test script:
```bash
chmod +x test_all_apis.sh
./test_all_apis.sh
```

## 11. Response Examples

### Successful ATS Analysis Response
```json
{
  "job_id": "ats_20240115_103045_abc123",
  "status": "completed",
  "timestamp": "2024-01-15T10:30:45Z",
  "processing_time": 2.34,
  "results": {
    "overall_score": 85,
    "keyword_matches": {
      "found": ["Python", "FastAPI", "Docker", "AWS"],
      "missing": ["Machine Learning", "Kubernetes"],
      "score": 75
    },
    "skills_analysis": {
      "technical_skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
      "soft_skills": ["Leadership", "Communication"],
      "relevance_score": 88
    },
    "recommendations": [
      "Add 'Machine Learning' keywords to improve match",
      "Include specific AWS services experience",
      "Add quantifiable achievements"
    ],
    "spacy_insights": {
      "entities": [
        {"text": "Python", "label": "SKILL", "confidence": 0.95},
        {"text": "AWS", "label": "TECHNOLOGY", "confidence": 0.92}
      ],
      "experience_duration": "5+ years",
      "education_level": "Master's Degree"
    }
  }
}
```

### Website Generation Response
```json
{
  "job_id": "web_20240115_103130_def456",
  "status": "completed",
  "timestamp": "2024-01-15T10:31:30Z",
  "website_url": "https://generated-site.zexplatform.com/def456",
  "preview_url": "https://preview.zexplatform.com/def456",
  "template": "modern",
  "theme": "professional",
  "features": {
    "responsive": true,
    "optimized": true,
    "seo_ready": true
  },
  "files": {
    "html": "index.html",
    "css": "styles.css",
    "js": "script.js"
  }
}
```

## 12. Troubleshooting

### Common Issues and Solutions

1. **Connection Refused**: Ensure the server is running on the correct port
2. **File Upload Errors**: Check file size limits and supported formats
3. **Timeout Issues**: Increase timeout for large file processing
4. **Rate Limiting**: Add delays between requests for bulk testing

### Debug Commands
```bash
# Check server logs
curl -X GET "${ZEX_BASE_URL}/api/v1/logs/recent" | jq '.'

# Validate API endpoints
curl -X GET "${ZEX_BASE_URL}/api/v1/docs"

# Test connectivity
curl -I "${ZEX_BASE_URL}/health"
```

---

## Summary

This comprehensive testing guide covers all ZeX Platform v3.0.0 services including:

- ✅ Enhanced ATS analysis with spaCy NLP
- ✅ Dynamic website generation with multiple templates
- ✅ Multi-format file processing
- ✅ Real-time analytics and monitoring
- ✅ Batch operations and concurrent processing
- ✅ Error handling and performance testing

For additional support, refer to the API documentation at `/api/v1/docs` or contact the development team.
