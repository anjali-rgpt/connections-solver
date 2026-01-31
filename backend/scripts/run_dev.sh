#!/bin/bash

# Connections Solver - Development Server Script
# Fully automated: installs UV, Python 3.11+, dependencies, and runs server

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Connections Solver - Development Server${NC}"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

# Step 1: Install UV if needed
if ! command -v uv &> /dev/null; then
    echo -e "${BLUE}Installing UV package manager...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add UV to PATH for this session
    export PATH="$HOME/.cargo/bin:$PATH"

    # Verify installation
    if ! command -v uv &> /dev/null; then
        echo -e "${YELLOW}UV installed but not in PATH. Trying common locations...${NC}"
        if [ -f "$HOME/.cargo/bin/uv" ]; then
            export PATH="$HOME/.cargo/bin:$PATH"
        fi
    fi

    echo -e "${GREEN}✓ UV installed${NC}"
else
    echo -e "${GREEN}✓ UV found${NC}"
fi

# Step 2: Ensure Python 3.11+ is available via UV
echo -e "${BLUE}Checking Python version...${NC}"

# Let UV install Python 3.11 if needed
if ! uv python list | grep -q "3.11"; then
    echo -e "${YELLOW}Python 3.11 not found. Installing via UV...${NC}"
    uv python install 3.11
    echo -e "${GREEN}✓ Python 3.11 installed${NC}"
else
    echo -e "${GREEN}✓ Python 3.11 available${NC}"
fi

# Step 3: Create virtual environment with Python 3.11
if [ -d ".venv" ]; then
    # Check if existing venv has correct Python version
    VENV_PYTHON_VERSION=$(.venv/bin/python --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    if [ "$(printf '%s\n' "3.11" "$VENV_PYTHON_VERSION" | sort -V | head -n1)" != "3.11" ]; then
        echo -e "${YELLOW}Existing .venv has Python $VENV_PYTHON_VERSION (need 3.11+). Recreating...${NC}"
        rm -rf .venv
    fi
fi

if [ ! -d ".venv" ]; then
    echo -e "${BLUE}Creating virtual environment with Python 3.11...${NC}"
    uv venv --python 3.11
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists with correct Python version${NC}"
fi

# Step 4: Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

# Step 5: Install dependencies to isolated .venv
echo -e "${BLUE}Installing dependencies (isolated to .venv)...${NC}"
uv pip install -e . --group dev
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 6: Create .env if needed
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Environment file created${NC}"
else
    echo -e "${GREEN}✓ Environment file exists${NC}"
fi

# All setup complete
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${GREEN}Server starting at http://localhost:8000${NC}"
echo -e "${GREEN}API docs at http://localhost:8000/docs${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Run the server
uvicorn src.connections_solver.main:app --reload --host 0.0.0.0 --port 8000
