#!/bin/bash

# ZeX-ATS-AI Deployment Script
# This script handles the complete deployment of the application

set -e  # Exit on any error

echo "🚀 Starting ZeX-ATS-AI Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p uploads logs static ssl
chmod 755 uploads logs static

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    print_warning "No .env file found. Copying from .env.example..."
    cp .env.example .env
    print_warning "Please edit .env file with your configuration before continuing."
    print_warning "Press Enter to continue after updating .env file..."
    read
fi

# Build and start services
print_status "Building Docker images..."
docker-compose build --no-cache

print_status "Starting services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Check if services are running
print_status "Checking service health..."

# Check main app
if curl -f http://localhost:8000/health &> /dev/null; then
    print_status "Main application is running"
else
    print_error "Main application failed to start"
    docker-compose logs app
    exit 1
fi

# Check database
if docker-compose exec -T db pg_isready -U zex_user -d zex_ats_db &> /dev/null; then
    print_status "Database is running"
else
    print_error "Database failed to start"
    docker-compose logs db
    exit 1
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping &> /dev/null; then
    print_status "Redis is running"
else
    print_error "Redis failed to start"
    docker-compose logs redis
    exit 1
fi

# Run database migrations
print_status "Running database migrations..."
docker-compose exec app python -c "
import asyncio
from src.core.database import DatabaseManager

async def migrate():
    db = DatabaseManager()
    await db.initialize()
    await db.create_tables()
    await db.close()
    print('Database migration completed')

asyncio.run(migrate())
"

# Create default admin user if specified
if [ ! -z "$ADMIN_EMAIL" ] && [ ! -z "$ADMIN_PASSWORD" ]; then
    print_status "Creating admin user..."
    docker-compose exec app python cli.py user create "$ADMIN_EMAIL" "$ADMIN_PASSWORD" --role admin --tier enterprise
fi

print_status "Deployment completed successfully! 🎉"
echo ""
echo "🌐 Application URLs:"
echo "   • Main Application: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • MinIO Console: http://localhost:9001 (admin/admin123)"
echo "   • Flower (Celery Monitor): http://localhost:5555"
echo "   • Grafana Dashboard: http://localhost:3001 (admin/admin123)"
echo "   • Prometheus: http://localhost:9090"
echo ""
echo "📋 Useful commands:"
echo "   • View logs: docker-compose logs -f"
echo "   • Stop services: docker-compose down"
echo "   • Restart services: docker-compose restart"
echo "   • CLI access: docker-compose exec app python cli.py --help"
echo ""
echo "📁 Important directories:"
echo "   • Uploads: ./uploads"
echo "   • Logs: ./logs"
echo "   • SSL certificates: ./ssl"
echo ""

# Show service status
print_status "Service Status:"
docker-compose ps
