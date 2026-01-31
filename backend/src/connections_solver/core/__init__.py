"""Core domain models and exceptions."""
from connections_solver.core.models import (
    Category,
    Solution,
    Puzzle,
    PredictedCategory,
    SolverResult,
    CategoryEvaluation,
    EvaluationMetrics,
    Evaluation,
)
from connections_solver.core.exceptions import (
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
