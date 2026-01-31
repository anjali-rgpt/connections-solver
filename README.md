# Connections Game Solver

A backend service for solving NYT Connections puzzles using AI.

## What is this?

Connections is a word puzzle game where you must group 16 words into 4 categories of 4 words each. This project provides an API to:
- Upload puzzles with their solutions
- Run different solver algorithms to attempt solving
- Evaluate solver performance against ground truth

## Why is this important?

This solver enables:
- **Algorithmic research** - Compare different solving strategies (random baseline, embedding-based, LLM-based)
- **Performance benchmarking** - Measure accuracy and efficiency of various AI approaches
- **Educational tool** - Understand how AI can approach semantic clustering problems

## How to run it

### Prerequisites
None! The script handles everything.

### One-command setup

```bash
./scripts/run_dev.sh
```

This script automatically:
- Installs UV package manager if needed
- Installs Python 3.11 if needed (via UV)
- Creates an isolated virtual environment (`.venv`)
- Installs all dependencies
- Starts the development server

The API will be available at `http://localhost:8000`

Interactive documentation: `http://localhost:8000/docs`

### Docker (alternative)

```bash
docker-compose up --build
```

## License

AGPL-3.0
