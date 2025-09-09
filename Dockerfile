# Multi-stage Docker build for ZeX Platform
# Production-ready container with all services integrated

# Stage 1: Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create build directory
WORKDIR /build

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage  
FROM python:3.11-slim

# Set production arguments
ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=4000
ENV NODE_ENV=production

# Install production system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    poppler-utils \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create application user
RUN useradd --create-home --shell /bin/bash zex
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads generated_websites logs data dashboard/assets \
    && chown -R zex:zex /app

# Install additional ML/NLP dependencies
RUN python -m pip install --no-cache-dir \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
    transformers sentence-transformers spacy nltk textblob textstat \
    opencv-python-headless Pillow pypdf2 python-docx openpyxl python-pptx \
    speechrecognition pydub beautifulsoup4 requests aiofiles httpx

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon'); nltk.download('wordnet')"

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Set up environment variables
ENV UPLOAD_DIR=/app/uploads
ENV GENERATED_WEBSITES_DIR=/app/generated_websites
ENV LOG_LEVEL=INFO
ENV DEBUG=False

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Switch to application user
USER zex

# Expose port
EXPOSE ${PORT}

# Start command with proper signal handling
CMD ["python", "zex_service.py"]
