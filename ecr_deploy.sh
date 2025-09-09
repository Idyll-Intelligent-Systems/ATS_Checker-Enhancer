#!/bin/bash

# ZeX Platform AWS ECR Deployment Script
# This script automates the complete deployment process to AWS ECR

set -e

echo "🚀 Starting ZeX Platform AWS ECR Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# AWS Configuration
AWS_REGION="eu-north-1"
ECR_REPOSITORY="879584802968.dkr.ecr.eu-north-1.amazonaws.com/zex"
IMAGE_NAME="zex"

echo -e "${YELLOW}Step 1: Checking AWS credentials...${NC}"
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}❌ AWS credentials not configured!${NC}"
    echo -e "${YELLOW}Please run: aws configure${NC}"
    echo "Required information:"
    echo "  - AWS Access Key ID"
    echo "  - AWS Secret Access Key"
    echo "  - Default region name: ${AWS_REGION}"
    echo "  - Default output format: json"
    exit 1
fi

echo -e "${GREEN}✅ AWS credentials verified!${NC}"

echo -e "${YELLOW}Step 2: Authenticating Docker with AWS ECR...${NC}"
if aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPOSITORY%%/*}; then
    echo -e "${GREEN}✅ Docker authenticated with AWS ECR!${NC}"
else
    echo -e "${RED}❌ Failed to authenticate with AWS ECR!${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 3: Checking if Docker image exists...${NC}"
if docker images ${IMAGE_NAME}:latest -q > /dev/null; then
    echo -e "${GREEN}✅ Docker image '${IMAGE_NAME}:latest' found!${NC}"
else
    echo -e "${YELLOW}⚠️  Docker image not found, building now...${NC}"
    echo -e "${YELLOW}Step 3a: Building Docker image...${NC}"
    docker build -t ${IMAGE_NAME} .
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
fi

echo -e "${YELLOW}Step 4: Tagging image for ECR repository...${NC}"
docker tag ${IMAGE_NAME}:latest ${ECR_REPOSITORY}:latest
echo -e "${GREEN}✅ Image tagged successfully!${NC}"

echo -e "${YELLOW}Step 5: Pushing image to AWS ECR...${NC}"
if docker push ${ECR_REPOSITORY}:latest; then
    echo -e "${GREEN}✅ Image pushed to ECR successfully!${NC}"
else
    echo -e "${RED}❌ Failed to push image to ECR!${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 6: Deployment Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 ZeX Platform Successfully Deployed to AWS ECR!${NC}"
echo ""
echo "📦 Repository: ${ECR_REPOSITORY}"
echo "🏷️  Tag: latest"
echo "🌍 Region: ${AWS_REGION}"
echo ""
echo "🚀 Next Steps:"
echo "1. Deploy to ECS cluster: arn:aws:ecs:eu-north-1:879584802968:cluster/Zex-platform"
echo "2. Update service with new image"
echo "3. Monitor deployment logs"
echo ""
echo "📝 Image Details:"
docker images ${ECR_REPOSITORY}:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "${GREEN}✨ Deployment completed successfully!${NC}"
