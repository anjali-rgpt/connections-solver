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
]
