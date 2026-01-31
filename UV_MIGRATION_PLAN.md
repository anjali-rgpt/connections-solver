# UV Package Manager Migration Plan

## Overview
Migrate from `pip` + `venv` to `uv` for faster, more reliable Python package management with project isolation.

## What is UV?
`uv` is an extremely fast Python package installer and resolver written in Rust by Astral (creators of Ruff). It's 10-100x faster than pip and provides:
- Fast dependency resolution
- Built-in virtual environment management
- Lock file support for reproducible builds
- Drop-in replacement for pip and pip-tools

## Migration Steps

### 1. Install UV

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using Homebrew
brew install uv

# Or using pip (ironic, but works)
pip install uv
```

### 2. Project Structure Changes

**Remove:**
- `.venv/` directory (if it exists)
- `requirements.txt` (will be replaced with `pyproject.toml`)

**Add:**
- `pyproject.toml` (modern Python project specification)
- `uv.lock` (lock file for reproducible builds - should be committed to git)

### 3. Create pyproject.toml

Replace `requirements.txt` with a proper `pyproject.toml`:

```toml
[project]
name = "connections-solver"
version = "0.1.0"
description = "Backend service for solving NYT Connections puzzles using AI"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "AGPL-3.0"}
dependencies = [
    "fastapi==0.109.0",
    "uvicorn[standard]==0.27.0",
    "pydantic==2.5.0",
    "pydantic-settings==2.1.0",
    "python-dotenv==1.0.0",
    "python-multipart==0.0.6",
]

[project.optional-dependencies]
dev = [
    "black==24.1.1",
    "ruff==0.1.14",
    "pylint==3.0.3",
    "flake8==7.0.0",
    "pytest==7.4.3",
    "pytest-asyncio==0.21.1",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = []

[tool.black]
line-length = 100
target-version = ['py310']

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
```

### 4. Initialize UV Project

```bash
# Navigate to project root
cd /Users/argcodes/code_repos/connections-solver

# Create virtual environment with uv
uv venv

# This creates a .venv directory that uv manages
```

### 5. Install Dependencies

```bash
# Install all dependencies (including dev)
uv pip install -e ".[dev]"

# Or install just production dependencies
uv pip install -e .

# Sync dependencies from pyproject.toml (ensures exact match)
uv pip sync pyproject.toml
```

### 6. Generate Lock File

```bash
# Create uv.lock file for reproducible builds
uv lock

# This locks all dependencies and their transitive dependencies
# Should be committed to version control
```

### 7. Update .gitignore

```bash
# Add to .gitignore if not already there
echo ".venv/" >> .gitignore

# Keep uv.lock committed for reproducibility
```

### 8. Update Development Scripts

**Update `scripts/run_dev.sh`:**

```bash
#!/bin/bash

# Connections Solver - Development Server Script (UV version)

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Connections Solver Development Server${NC}"

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV not found. Installing...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment with uv...${NC}"
    uv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/sync dependencies
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
```

### 9. Update Dockerfile for UV

**Option A: Use UV in Docker (Recommended)**

```dockerfile
# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock* ./
COPY src/ ./src/
COPY data/ ./data/

# Install dependencies using uv
RUN uv pip install --system -e .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.connections_solver.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Option B: Multi-stage Docker Build (Smaller Image)**

```dockerfile
# Build stage
FROM python:3.10-slim AS builder

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Create virtual environment and install dependencies
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install -e .

# Runtime stage
FROM python:3.10-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY src/ ./src/
COPY data/ ./data/

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.connections_solver.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 10. Update README.md

Add UV instructions to README:

```markdown
## Setup with UV (Recommended)

### Prerequisites
- Python 3.10+
- UV package manager

### Install UV
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Quick Start
```bash
# Clone the repository
git clone https://github.com/anjali-rgpt/connections-solver.git
cd connections-solver

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Run the development server
./scripts/run_dev.sh
```

### Adding New Dependencies
```bash
# Add a production dependency
uv pip install <package-name>

# Update pyproject.toml
# Then lock dependencies
uv lock
```
```

## Benefits of UV Migration

### Performance
- **10-100x faster** than pip for dependency resolution
- Parallel downloads and installations
- Efficient caching

### Reliability
- Reproducible builds with lock files
- Better dependency resolution algorithm
- Consistent across environments

### Developer Experience
- Faster local development (quicker `pip install`)
- Faster CI/CD builds
- Built-in virtual environment management
- Compatible with existing pip workflows

## Common UV Commands

```bash
# Create virtual environment
uv venv

# Install package
uv pip install <package>

# Install from requirements/pyproject
uv pip install -r requirements.txt
uv pip install -e ".[dev]"

# Sync dependencies (match exactly)
uv pip sync pyproject.toml

# Lock dependencies
uv lock

# Compile dependencies (like pip-compile)
uv pip compile pyproject.toml -o requirements.txt

# List installed packages
uv pip list

# Show package info
uv pip show <package>

# Uninstall package
uv pip uninstall <package>
```

## Migration Checklist

- [ ] Install UV locally
- [ ] Create `pyproject.toml` from `requirements.txt`
- [ ] Remove old `.venv` directory
- [ ] Initialize UV: `uv venv`
- [ ] Install dependencies: `uv pip install -e ".[dev]"`
- [ ] Generate lock file: `uv lock`
- [ ] Update `scripts/run_dev.sh` to use UV
- [ ] Update Dockerfile to use UV
- [ ] Update README.md with UV instructions
- [ ] Update `.gitignore` (ensure `uv.lock` is NOT ignored)
- [ ] Test locally: `./scripts/run_dev.sh`
- [ ] Test Docker: `docker-compose up --build`
- [ ] Commit changes: `pyproject.toml`, `uv.lock`, updated scripts

## Rollback Plan

If issues arise, you can easily rollback:

```bash
# Remove UV artifacts
rm -rf .venv uv.lock

# Reinstall with pip
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Notes

- **Virtual Environment Naming**: UV creates `.venv` by default, which is the standard name. This avoids confusion and works well with most IDE auto-detection.
- **Lock Files**: Always commit `uv.lock` to ensure reproducible builds across development, staging, and production.
- **CI/CD**: Update CI/CD pipelines to install UV before running tests.
- **Team Coordination**: Ensure all team members install UV and understand the new workflow.

## Resources

- [UV Documentation](https://github.com/astral-sh/uv)
- [UV vs Pip Performance Benchmarks](https://github.com/astral-sh/uv#benchmarks)
- [Modern Python Project Setup](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
