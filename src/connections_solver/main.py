"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from connections_solver.config import settings
from connections_solver.logging_config import setup_logging, get_logger
from connections_solver.api.routes import puzzles, solver, evaluation

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Initialize solvers (triggers registration)
import connections_solver.solvers  # noqa: F401

# Create FastAPI application
app = FastAPI(
    title="Connections Solver API",
    description="Backend service for solving NYT Connections puzzles using AI",
    version="0.1.0",
)

logger.info("Starting Connections Solver API")
logger.info(f"Environment: {settings.environment}")
logger.info(f"Log level: {settings.log_level}")

# Configure CORS
cors_origins = settings.get_cors_origins_list()
logger.info(f"CORS origins: {cors_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(puzzles.router, prefix="/api/v1")
app.include_router(solver.router, prefix="/api/v1")
app.include_router(evaluation.router, prefix="/api/v1")


@app.get("/")
def root():
    """Root endpoint.

    Returns:
        Welcome message with API information
    """
    return {
        "message": "Connections Solver API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
def health_check():
    """Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy"}
