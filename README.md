# Connections Game Solver

Backend service for solving NYT Connections puzzles using AI.

## Quick Start

### Option 1: Using Shell Script (Recommended for Development)

```bash
# Run the development server (creates .venv automatically)
./scripts/run_dev.sh
```

The script will:
- Create a virtual environment (`.venv`) if it doesn't exist
- Install all dependencies
- Create `.env` from `.env.example` if needed
- Start the server at `http://localhost:8000`

### Option 2: Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run in detached mode
docker-compose up -d
```

### Option 3: Manual Setup

1. Create a virtual environment (use any name you prefer):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```

4. Run the development server:
```bash
uvicorn src.connections_solver.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage Examples

### 1. Create a Puzzle

```bash
curl -X POST http://localhost:8000/api/v1/puzzles \
  -H "Content-Type: application/json" \
  -d @data/samples/example_puzzle.json
```

### 2. List All Puzzles

```bash
curl http://localhost:8000/api/v1/puzzles
```

### 3. Solve a Puzzle

```bash
curl -X POST http://localhost:8000/api/v1/solve \
  -H "Content-Type: application/json" \
  -d '{
    "puzzle_id": "<puzzle-id-from-step-1>",
    "solver_type": "random"
  }'
```

### 4. Evaluate Solver Performance

```bash
curl -X POST http://localhost:8000/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "solve_id": "<solve-id-from-step-3>"
  }'
```

### 5. List Available Solvers

```bash
curl http://localhost:8000/api/v1/solvers
```

## Project Structure

```
connections-solver/
├── src/connections_solver/    # Main application package
│   ├── api/                   # API routes and models
│   ├── core/                  # Domain models and exceptions
│   ├── solvers/               # Solver implementations
│   ├── storage/               # Storage layer
│   └── evaluation/            # Evaluation metrics
├── data/samples/              # Sample puzzles
└── requirements.txt           # Python dependencies
```

## License

AGPL-3.0
