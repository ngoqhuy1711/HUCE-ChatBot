#!/bin/bash
# =============================================================================
# Deployment Script - HUCE Chatbot
# =============================================================================
# Script này giúp deploy chatbot lên server production

set -e  # Exit on error

echo "========================================="
echo "HUCE Chatbot - Deployment Script"
echo "========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

print_success "Docker is installed"

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_success "Docker Compose is installed"

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    print_warning ".env.production not found. Please create it from .env.production template"
    exit 1
fi

print_success ".env.production found"

# Stop existing containers
echo ""
echo "Stopping existing containers..."
docker-compose down || true
print_success "Containers stopped"

# Build images
echo ""
echo "Building Docker images..."
docker-compose build --no-cache
print_success "Images built successfully"

# Start containers
echo ""
echo "Starting containers..."
docker-compose up -d
print_success "Containers started"

# Wait for services to be healthy
echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check backend health
echo "Checking backend health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend is healthy"
else
    print_error "Backend is not healthy"
    docker-compose logs backend
    exit 1
fi

# Check frontend health
echo "Checking frontend health..."
if curl -f http://localhost:3000/ > /dev/null 2>&1; then
    print_success "Frontend is healthy"
else
    print_warning "Frontend might still be starting up..."
fi

# Show running containers
echo ""
echo "Running containers:"
docker-compose ps

echo ""
echo "========================================="
print_success "Deployment completed successfully!"
echo "========================================="
echo ""
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:3000"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"

