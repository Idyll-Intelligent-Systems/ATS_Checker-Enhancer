#!/bin/bash

# Dynamic Portfolio Website Generator - Quick Setup Script
# This script sets up the environment for generating portfolio websites

set -e

echo "🚀 Setting up Dynamic Portfolio Website Generator..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check if Python 3 is installed
print_header "Checking System Requirements"
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_status "Found Python $PYTHON_VERSION"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

# Install required Python packages
print_header "Installing Required Packages"
print_status "Installing basic dependencies..."

# Create requirements file for the dynamic website generator
cat > /tmp/website_generator_requirements.txt << EOF
# Basic requirements for Dynamic Website Generator
PyPDF2>=3.0.1
python-docx>=0.8.11
fastapi>=0.104.0
uvicorn>=0.24.0
python-multipart>=0.0.6
aiofiles>=23.2.1
EOF

pip3 install -r /tmp/website_generator_requirements.txt --user --quiet

print_status "Dependencies installed successfully!"

# Create necessary directories
print_header "Setting up Directory Structure"
mkdir -p generated_websites
mkdir -p logs
mkdir -p uploads

print_status "Directories created successfully!"

# Set executable permissions
print_header "Setting Permissions"
chmod +x dynamic_website_generator.py
chmod +x website_generator_api.py

print_status "Permissions set successfully!"

# Test the installation
print_header "Testing Installation"
if python3 dynamic_website_generator.py --help &> /dev/null; then
    print_status "Command-line tool working correctly!"
else
    print_warning "Command-line tool may have issues. Check dependencies."
fi

# Create a sample resume for testing
print_header "Creating Sample Files"
cat > sample_resume.txt << 'EOF'
John Doe
Software Engineer

Contact Information:
Email: john.doe@email.com
Phone: +1-555-0123
Location: San Francisco, CA
LinkedIn: linkedin.com/in/johndoe
GitHub: github.com/johndoe

Professional Summary:
Experienced software engineer with 5 years in full-stack development.
Proficient in Python, JavaScript, and cloud technologies.
Strong background in system design and scalable architecture.

Technical Skills:
- Languages: Python, JavaScript, TypeScript, Java
- Frameworks: React, Node.js, Django, FastAPI  
- Cloud: AWS, Docker, Kubernetes
- Databases: PostgreSQL, MongoDB, Redis
- Tools: Git, CI/CD, Terraform

Professional Experience:

Software Engineer | Tech Company | 2020 - Present
- Developed scalable web applications serving 100K+ users
- Led migration to microservices architecture
- Implemented automated testing and deployment pipelines
- Collaborated with cross-functional teams on product features

Junior Developer | Startup Inc | 2018 - 2020
- Built responsive web applications using modern frameworks
- Optimized database queries improving performance by 40%
- Participated in code reviews and agile development processes

Education:
Bachelor of Computer Science | University Name | 2014 - 2018

Projects:
E-commerce Platform - Full-stack web application with payment integration
Data Analytics Dashboard - Real-time analytics using Python and React
Mobile App Backend - RESTful API serving iOS/Android applications
EOF

print_status "Sample resume created: sample_resume.txt"

# Generate a test website
print_header "Generating Test Website"
if python3 dynamic_website_generator.py sample_resume.txt --output test-portfolio --theme modern --zip; then
    print_status "Test website generated successfully!"
    
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📁 Generated test website: generated_websites/test-portfolio/"
    echo "📦 Download package: generated_websites/test-portfolio.zip"
    echo ""
    echo "🚀 Quick Start Commands:"
    echo ""
    echo "1. Generate website from resume:"
    echo "   python3 dynamic_website_generator.py your_resume.pdf --output my-portfolio"
    echo ""
    echo "2. Start web API server:"
    echo "   python3 website_generator_api.py"
    echo ""
    echo "3. Preview generated website:"
    echo "   python3 dynamic_website_generator.py --preview generated_websites/test-portfolio"
    echo ""
    echo "4. Open web interface:"
    echo "   open website_generator_ui.html"
    echo ""
    echo "📚 Documentation: DYNAMIC_WEBSITE_README.md"
    echo ""
else
    print_error "Failed to generate test website. Please check the logs above."
    exit 1
fi

# Cleanup
rm -f /tmp/website_generator_requirements.txt

print_status "Setup completed! You're ready to generate amazing portfolio websites! 🌟"
