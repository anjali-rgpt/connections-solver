"""Pydantic models for API responses."""

from typing import List, Dict, Any
from pydantic import BaseModel

from ...core.models import (
    Puzzle,
    SolverResult,
    Evaluation,
)


class PuzzleListResponse(BaseModel):
    """Response model for listing puzzles.

    Attributes:
        puzzles: List of puzzles
        total: Total number of puzzles (for pagination)
        limit: Maximum number of results returned
        offset: Number of results skipped
    """

    puzzles: List[Puzzle]
    total: int
    limit: int
    offset: int


class SolverInfoResponse(BaseModel):
    """Response model for solver information.

    Attributes:
        name: Solver name
        description: Human-readable description
        config_schema: JSON schema for configuration
    """

    name: str
    description: str
    config_schema: Dict[str, Any]


class SolverListResponse(BaseModel):
    """Response model for listing available solvers.

    Attributes:
        solvers: List of available solvers with their info
    """

    solvers: List[SolverInfoResponse]


class EvaluationListResponse(BaseModel):
    """Response model for listing evaluations.

    Attributes:
        evaluations: List of evaluations
        total: Total number of evaluations (for pagination)
        limit: Maximum number of results returned
        offset: Number of results skipped
    """

    evaluations: List[Evaluation]
    total: int
    limit: int
    offset: int


class ErrorResponse(BaseModel):
    """Response model for error messages.

    Attributes:
        detail: Error message description
    """

    detail: str
