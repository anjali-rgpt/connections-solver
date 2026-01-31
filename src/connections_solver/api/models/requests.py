"""Pydantic models for API request validation."""

from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from connections_solver.core.models import Solution


class CreatePuzzleRequest(BaseModel):
    """Request model for creating a new puzzle.

    Attributes:
        words: List of exactly 16 words
        solution: The correct grouping into 4 categories
        metadata: Optional metadata (source, date, etc.)
    """

    words: list[str] = Field(..., min_length=16, max_length=16)
    solution: Solution
    metadata: Optional[Dict[str, Any]] = None


class SolveRequest(BaseModel):
    """Request model for solving a puzzle.

    Attributes:
        puzzle_id: ID of the puzzle to solve
        solver_type: Name of solver to use (e.g., "random")
        solver_config: Optional solver-specific configuration
    """

    puzzle_id: UUID
    solver_type: str
    solver_config: Optional[Dict[str, Any]] = None


class EvaluateRequest(BaseModel):
    """Request model for evaluating a solver result.

    Attributes:
        solve_id: ID of the solver result to evaluate
    """

    solve_id: UUID
