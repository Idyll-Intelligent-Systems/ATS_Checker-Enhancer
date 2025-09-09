#!/bin/bash

# ZeX Platform Docker Build and Deploy Script
# Comprehensive build script for containerization and AWS deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="zex"
AWS_REGION="eu-north-1"
AWS_ACCOUNT_ID="879584802968"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
ECR_REPOSITORY="${ECR_REGISTRY}/${PROJECT_NAME}"
IMAGE_TAG="latest"
PORT="4000"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_warning "AWS CLI is not installed - skipping AWS operations"
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        log_warning "Git is not installed - skipping GitHub operations"
    fi
    
    log_success "Prerequisites check completed"
}

# Clean up previous builds
cleanup() {
    log_info "Cleaning up previous builds..."
    
    # Remove dangling images
    docker image prune -f || true
    
    # Remove stopped containers
    docker container prune -f || true
    
    log_success "Cleanup completed"
}

# Build Docker image
build_image() {
    log_info "Building Docker image: ${PROJECT_NAME}:${IMAGE_TAG}"
    
    # Build with progress output
    docker build \
        --tag "${PROJECT_NAME}:${IMAGE_TAG}" \
        --tag "${ECR_REPOSITORY}:${IMAGE_TAG}" \
        --build-arg PORT=${PORT} \
        --progress=plain \
        .
    
    log_success "Docker image built successfully"
}

# Test image locally
test_image() {
    log_info "Testing Docker image locally..."
    
    # Stop any existing container
    docker stop zex-test 2>/dev/null || true
    docker rm zex-test 2>/dev/null || true
    
    # Run container in background
    docker run -d \
        --name zex-test \
        --publish ${PORT}:${PORT} \
        --env PORT=${PORT} \
        --env DEBUG=false \
        --env LOG_LEVEL=INFO \
        --volume "$(pwd)/uploads:/app/uploads" \
        --volume "$(pwd)/generated_websites:/app/generated_websites" \
        "${PROJECT_NAME}:${IMAGE_TAG}"
    
    # Wait for startup
    sleep 15
    
    # Test health endpoint
    if curl -f "http://localhost:${PORT}/health" > /dev/null 2>&1; then
        log_success "Health check passed"
    else
        log_error "Health check failed"
        docker logs zex-test
        docker stop zex-test
        docker rm zex-test
        exit 1
    fi
    
    # Clean up test container
    docker stop zex-test
    docker rm zex-test
    
    log_success "Local testing completed successfully"
}

# Authenticate with ECR
authenticate_ecr() {
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is required for ECR operations"
        return 1
    fi
    
    log_info "Authenticating with AWS ECR..."
    
    # Get ECR login token and authenticate Docker
    aws ecr get-login-password --region ${AWS_REGION} | \
        docker login --username AWS --password-stdin ${ECR_REGISTRY}
    
    log_success "ECR authentication successful"
}

# Push to ECR
push_to_ecr() {
    log_info "Pushing image to ECR: ${ECR_REPOSITORY}:${IMAGE_TAG}"
    
    # Push the image
    docker push "${ECR_REPOSITORY}:${IMAGE_TAG}"
    
    log_success "Image pushed to ECR successfully"
}

# Push to GitHub
push_to_github() {
    if ! command -v git &> /dev/null; then
        log_error "Git is required for GitHub operations"
        return 1
    fi
    
    log_info "Pushing code changes to GitHub..."
    
    # Check if there are changes to commit
    if [[ -n $(git status --porcelain) ]]; then
        # Add all changes
        git add .
        
        # Commit with timestamp
        COMMIT_MSG="Deploy ZeX Platform v3.0.0 - $(date '+%Y-%m-%d %H:%M:%S')"
        git commit -m "${COMMIT_MSG}"
        
        # Push to main branch
        git push origin main
        
        log_success "Code pushed to GitHub successfully"
    else
        log_info "No changes to commit"
    fi
}

# Main execution flow
main() {
    echo "🚀 ZeX Platform Docker Build and Deploy Script"
    echo "=============================================="
    
    # Check command line arguments
    case "${1:-build}" in
        "build")
            check_prerequisites
            cleanup
            build_image
            ;;
        "test")
            test_image
            ;;
        "push")
            authenticate_ecr
            push_to_ecr
            push_to_github
            ;;
        "all")
            check_prerequisites
            cleanup
            build_image
            test_image
            authenticate_ecr
            push_to_ecr
            push_to_github
            ;;
        *)
            echo "Usage: $0 [build|test|push|all]"
            echo "  build  - Build Docker image"
            echo "  test   - Test image locally"
            echo "  push   - Push to ECR and GitHub"
            echo "  all    - Run complete pipeline"
            exit 1
            ;;
    esac
    
    log_success "🎉 ZeX Platform deployment step completed successfully!"
}

# Execute main function
main "$@"
