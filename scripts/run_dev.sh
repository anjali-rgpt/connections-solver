#!/bin/bash

# Connections Solver - Development Server Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Connections Solver Development Server${NC}"

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating .venv...${NC}"
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

# Run the server
echo -e "${GREEN}Starting server at http://localhost:8000${NC}"
echo "API docs available at http://localhost:8000/docs"
echo ""
uvicorn src.connections_solver.main:app --reload --host 0.0.0.0 --port 8000
