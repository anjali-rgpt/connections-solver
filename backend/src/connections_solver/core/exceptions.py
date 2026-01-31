"""Custom exceptions for the Connections Solver application."""


class PuzzleNotFoundError(Exception):
    """Raised when a puzzle is not found in storage."""


class SolveNotFoundError(Exception):
    """Raised when a solver result is not found in storage."""


class EvaluationNotFoundError(Exception):
    """Raised when an evaluation is not found in storage."""


class InvalidPuzzleError(Exception):
    """Raised when puzzle data is invalid."""


class SolverNotFoundError(Exception):
    """Raised when a requested solver is not registered."""


class InvalidSolverConfigError(Exception):
    """Raised when solver configuration is invalid."""
