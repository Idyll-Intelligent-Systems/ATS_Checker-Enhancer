#!/bin/bash

# ZeX-ATS-AI Development Setup Script
# Quick setup for local development

set -e

echo "🔧 Setting up ZeX-ATS-AI for development..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check Python version
if ! python3 --version | grep -E "Python 3\.(9|10|11)" &> /dev/null; then
    print_warning "Python 3.9+ is recommended. Current version:"
    python3 --version
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file..."
    cp .env.example .env
fi

# Create necessary directories
print_status "Creating directories..."
mkdir -p uploads logs static tests/test_uploads

# Set permissions
chmod 755 uploads logs static

print_status "Development setup completed! 🎉"
echo ""
echo "🚀 To start development:"
echo "   1. Activate the virtual environment: source venv/bin/activate"
echo "   2. Edit .env file with your configuration"
echo "   3. Start the development server: uvicorn src.main:app --reload --port 8000"
echo ""
echo "📋 Other useful commands:"
echo "   • Run tests: python -m pytest tests/ -v"
echo "   • CLI tool: python cli.py --help"
echo "   • Format code: black src/ tests/"
echo "   • Lint code: flake8 src/ tests/"
echo ""
echo "📚 Documentation:"
echo "   • API docs (when running): http://localhost:8000/docs"
echo "   • ReDoc: http://localhost:8000/redoc"
