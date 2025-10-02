#!/bin/bash

# Argo Aviation Referral Portal - Docker Deployment Script
echo "🚀 Deploying Argo Aviation Referral Portal with Docker..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

print_status "Stopping any existing containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

print_status "Building Docker image..."
if docker-compose build || docker compose build; then
    print_success "Docker image built successfully!"
else
    print_error "Failed to build Docker image"
    exit 1
fi

print_status "Starting containers..."
if docker-compose up -d || docker compose up -d; then
    print_success "Containers started successfully!"
else
    print_error "Failed to start containers"
    exit 1
fi

# Wait for the application to start
print_status "Waiting for application to start..."
sleep 10

# Check if the application is running
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    print_success "✅ Argo Aviation Referral Portal is running!"
    echo ""
    echo "🌐 Application URL: http://localhost:8000"
    echo "👤 Admin Login:"
    echo "   📧 Email: admin@argo-aviation.com"
    echo "   🔑 Password: admin123"
    echo ""
    echo "📊 Container Status:"
    docker-compose ps || docker compose ps
    echo ""
    echo "📝 To view logs: docker-compose logs -f"
    echo "🛑 To stop: docker-compose down"
else
    print_warning "Application might still be starting up..."
    print_status "Check logs with: docker-compose logs -f"
fi

print_success "Deployment completed!"
