#!/bin/bash

# MakingConnectionsAI - Unified Docker Deployment Script
# Deploys both frontend and backend in Docker containers

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}MakingConnectionsAI - Development Deployment${NC}"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Error: Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${BLUE}Building and starting Docker containers...${NC}"
echo ""

# Build and start containers
docker-compose up --build

# Note: docker-compose up will handle:
# - Building backend container (Python + FastAPI)
# - Building frontend container (Node + React + Vite)
# - Creating network between containers
# - Exposing ports (8000 for backend, 5173 for frontend)
# - Mounting volumes for hot-reload during development
