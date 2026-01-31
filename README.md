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
- Python 3.11+
- [UV package manager](https://github.com/astral-sh/uv)

### Installation

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run the development server
./scripts/run_dev.sh
```

The API will be available at `http://localhost:8000`

Interactive documentation: `http://localhost:8000/docs`

### Docker (alternative)

```bash
docker-compose up --build
```

## License

AGPL-3.0
