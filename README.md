# MakingConnectionsAI

A full-stack AI application for solving NYT Connections puzzles with multiple solver algorithms and real-time evaluation.

## What is this?

Connections is a word puzzle game where you must group 16 words into 4 categories of 4 words each. This project provides:

- **Modern Web Interface** - React + TypeScript frontend for creating and solving puzzles
- **FastAPI Backend** - RESTful API for puzzle management and solver execution
- **Multiple Solvers** - Compare different AI approaches (random baseline, embedding-based, LLM-based)
- **Real-time Evaluation** - Automatic performance metrics (accuracy, precision, recall, F1 scores)
- **Parallel Execution** - Run all solvers simultaneously for fast results

## Tech Stack

### Frontend
- **React** - UI library
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first styling
- **Vite** - Fast build tool
- **Zustand** - State management
- **TanStack Query** - Data fetching and caching

### Backend
- **FastAPI** - Python web framework
- **SQLAlchemy** - ORM for persistence
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## Project Structure

```
connections-solver/
├── backend/              # Python FastAPI backend
│   ├── src/connections_solver/
│   ├── tests/
│   ├── scripts/
│   ├── data/
│   └── Dockerfile
├── frontend/             # React TypeScript frontend
│   ├── src/
│   │   ├── api/         # API client layer
│   │   ├── components/  # UI components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── stores/      # State management
│   │   ├── types/       # TypeScript definitions
│   │   └── utils/       # Utility functions
│   ├── public/
│   └── Dockerfile
├── scripts/
│   └── run_dev.sh       # Unified deployment script
├── docker-compose.yml   # Multi-service orchestration
└── README.md            # This file
```

## Quick Start

### Prerequisites

**For Docker deployment (recommended):**
- Docker and Docker Compose

**For local development:**
- Python 3.11+
- Node.js 20+

### One-Command Deployment (Docker)

```bash
# Install frontend dependencies first
cd frontend
npm install
cd ..

# Start both frontend and backend
./scripts/run_dev.sh
```

This will start:
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Local Development (without Docker)

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
uvicorn src.connections_solver.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## How to Use

### Creating a Puzzle

1. Open http://localhost:5173
2. Click the sidebar toggle (← arrow) to open the puzzle form
3. Enter 4 categories, each with:
   - Category name (e.g., "Types of Fish")
   - 4 words for that category
4. Click "Create & Solve"

### What Happens Next

The app will automatically:
1. Create the puzzle via API
2. Execute all available solvers **in parallel**
3. Display results as each solver completes:
   - Shuffled 4×4 word grid
   - Color-coded categories (yellow, green, blue, purple)
   - Execution time
   - Evaluation metrics

### Understanding the Results

Each solver shows:
- **Accuracy**: Overall correctness (0-100%)
- **Word Accuracy**: Fraction of words in correct categories
- **Category Matches**: Number of perfectly matched categories (0-4)
- **Exact Match**: Whether all 4 categories were perfect
- **Per-Category Scores**: Precision, recall, and F1 for each category

### Example Puzzle

**Category 1: Types of Fish**
- salmon, tuna, bass, trout

**Category 2: Programming Languages**
- python, java, rust, go

**Category 3: Colors**
- red, blue, green, yellow

**Category 4: US States**
- texas, ohio, maine, utah

## Architecture Highlights

### Modular Frontend

- **Separation of Concerns**: API, state, hooks, and UI are isolated
- **Type Safety**: Full TypeScript coverage with comprehensive types
- **Component Encapsulation**: Each component in its own folder with types and utilities
- **Clean Exports**: Public APIs exposed via `index.ts` files

### State Management Flow

1. User creates puzzle → `usePuzzle` hook → API call
2. Backend creates puzzle → Returns puzzle ID
3. Frontend triggers all solvers in parallel using `Promise.allSettled()`
4. Each solver updates Zustand store independently
5. UI re-renders as state changes

### Parallel Solver Execution

```typescript
const solveWithAllSolvers = async (solvers: SolverInfo[]) => {
  const promises = solvers.map((solver) => solvePuzzle(solver.name));
  await Promise.allSettled(promises);
};
```

This ensures:
- All solvers run simultaneously
- No blocking on slow solvers
- Independent error handling
- Results appear as they complete

## API Endpoints

### Puzzles
- `POST /api/v1/puzzles` - Create a new puzzle
- `GET /api/v1/puzzles/{id}` - Retrieve a puzzle

### Solvers
- `GET /api/v1/solvers` - List available solver types
- `POST /api/v1/solve` - Execute a solver on a puzzle

### Evaluation
- `POST /api/v1/evaluate` - Evaluate solver performance

Full API documentation: http://localhost:8000/docs

## Configuration

### Backend Configuration

Edit `backend/.env`:

```bash
# CORS origins (frontend URLs)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Storage type: "memory" or "sqlite"
STORAGE_TYPE=memory

# Database path (only for sqlite)
DATABASE_PATH=data/connections.db

# Logging level
LOG_LEVEL=INFO
```

### Frontend Configuration

Edit `frontend/vite.config.ts` for API proxy settings.

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Type Checking
```bash
cd frontend
npm run build
```

### Manual Testing
See `DEPLOYMENT_CHECKLIST.md` for comprehensive testing guide.

## Documentation

- **FRONTEND_README.md** - Frontend architecture and component guide
- **DEPLOYMENT_CHECKLIST.md** - Deployment and testing checklist
- **UV_MIGRATION_PLAN.md** - UV package manager migration notes

## Why is this important?

This project enables:

- **Algorithmic Research** - Compare different solving strategies
- **Performance Benchmarking** - Measure AI approach effectiveness
- **Educational Tool** - Understand semantic clustering and AI reasoning
- **Real-World Application** - Production-ready full-stack architecture
- **Extensibility** - Easy to add new solvers and features

## Future Enhancements

1. **Solver Observability** - Display step-by-step reasoning
2. **Puzzle History** - Browse and replay previous puzzles
3. **Solver Comparison** - Side-by-side performance charts
4. **LLM Integration** - Advanced language model solvers
5. **Authentication** - User accounts and saved puzzles
6. **Custom Parameters** - Configure solver options in UI
7. **Real-time Updates** - WebSocket for live solver progress

## Troubleshooting

### Frontend won't connect to backend
- Check CORS in `backend/.env`: `CORS_ORIGINS=http://localhost:5173`
- Verify backend running: `curl http://localhost:8000/api/v1/solvers`
- Check Vite proxy in `frontend/vite.config.ts`

### Docker build fails
```bash
# Install frontend dependencies BEFORE Docker build
cd frontend
npm install
cd ..

# Rebuild containers
docker-compose down
docker-compose up --build
```

### Solvers stuck loading
- Check backend logs: `docker-compose logs backend`
- Check browser console for errors
- Verify solvers available: `curl http://localhost:8000/api/v1/solvers`

See `DEPLOYMENT_CHECKLIST.md` for more troubleshooting tips.

## Contributing

When adding features:
1. Follow existing modular structure
2. Add TypeScript types for all new code
3. Write JSDoc comments for public APIs
4. Test both frontend and backend
5. Update documentation

## License

AGPL-3.0 - See LICENSE file for details

---

**Built with modern best practices for maintainability, scalability, and developer experience.**
