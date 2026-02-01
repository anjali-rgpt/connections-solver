"""Core domain models and exceptions."""
from .models import (
    Category,
    Solution,
    Puzzle,
    PredictedCategory,
    SolverResult,
    CategoryEvaluation,
    EvaluationMetrics,
    Evaluation,
)
from .exceptions import (
    SolverNotFoundError,
    PuzzleNotFoundError,
    ExternalPuzzleSourceError,
    PuzzleFormatError,
)

__all__ = [
    "Category",
    "Solution",
    "Puzzle",
    "PredictedCategory",
    "SolverResult",
    "CategoryEvaluation",
    "EvaluationMetrics",
    "Evaluation",
    "SolverNotFoundError",
    "PuzzleNotFoundError",
    "ExternalPuzzleSourceError",
    "PuzzleFormatError",
]
