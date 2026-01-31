#!/bin/bash

# Connections Solver - Development Server Script (UV)

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Connections Solver Development Server${NC}"

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: UV is not installed${NC}"
    echo -e "${YELLOW}Install UV with: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    echo -e "${YELLOW}Or visit: https://github.com/astral-sh/uv${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${YELLOW}Warning: Python $PYTHON_VERSION detected. Python 3.11+ is required.${NC}"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment with uv...${NC}"
    uv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Sync dependencies (fast!)
echo "Syncing dependencies with uv..."
uv pip install -e ".[dev]"

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
