#!/bin/bash

# ZeX-ATS-AI Enterprise Setup Script
# This script sets up the complete enterprise environment

set -e

echo "🚀 Setting up ZeX-ATS-AI Enterprise System..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data
echo "🔤 Downloading NLTK data..."
python -c "
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('vader_sentiment')
"

# Download spaCy models
echo "🧠 Downloading spaCy models..."
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p data/{uploads,processed,reports}
mkdir -p logs
mkdir -p config
mkdir -p tests
mkdir -p docs

# Initialize database (PostgreSQL)
echo "🗄️  Initializing database..."
python -c "
from src.database.models import create_tables
create_tables()
print('Database tables created successfully!')
"

# Start Redis server (if not running)
echo "🔴 Starting Redis server..."
redis-server --daemonize yes || echo "Redis may already be running"

# Create Docker network
echo "🐳 Setting up Docker network..."
docker network create zex-ats-network || echo "Network may already exist"

echo "✅ ZeX-ATS-AI setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Configure environment variables in .env file"
echo "2. Start the web application: python -m src.web.main"
echo "3. Start the Streamlit dashboard: streamlit run src/dashboard/app.py"
echo "4. Access the API documentation at http://localhost:8000/docs"
echo ""
echo "🌟 Welcome to ZeX-ATS-AI Enterprise!"
