# Multi-stage Docker build for ZeX Platform
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd --create-home --shell /bin/bash zex

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p \
    uploads \
    generated_websites \
    logs \
    data \
    dashboard/assets \
    && chown -R zex:zex /app

# Install basic additional dependencies including spaCy
RUN python -m pip install --no-cache-dir \
    nltk textblob textstat spacy \
    opencv-python-headless Pillow pypdf2 python-docx openpyxl python-pptx \
    speechrecognition pydub beautifulsoup4 requests aiofiles httpx

# Download NLTK and spaCy data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon'); nltk.download('wordnet')" || echo "NLTK downloads failed, continuing..."
RUN python -m spacy download en_core_web_sm || echo "spaCy model download failed, continuing..."

# Set up environment variables
ENV UPLOAD_DIR=/app/uploads
ENV GENERATED_WEBSITES_DIR=/app/generated_websites
ENV LOG_LEVEL=INFO
ENV DEBUG=False
ENV PORT=4000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Switch to application user
USER zex

# Expose port
EXPOSE ${PORT}

# Start command
CMD ["python", "zex_service.py"]
