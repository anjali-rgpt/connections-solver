"""Abstract base class for storage implementations."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..core.models import Puzzle, SolverResult, Evaluation


class BaseStorage(ABC):
    """Abstract interface for storage backends.

    This defines the contract that all storage implementations must follow.
    Implementations can use in-memory storage, SQLite, PostgreSQL, etc.
    """

    @abstractmethod
    def store_puzzle(self, puzzle: Puzzle) -> Puzzle:
        """Store a puzzle in the storage backend.

        Args:
            puzzle: The puzzle to store

        Returns:
            The stored puzzle (with any backend-assigned fields)
        """

    @abstractmethod
    def get_puzzle(self, puzzle_id: UUID) -> Optional[Puzzle]:
        """Retrieve a puzzle by its ID.

        Args:
            puzzle_id: The unique identifier of the puzzle

        Returns:
            The puzzle if found, None otherwise
        """

    @abstractmethod
    def list_puzzles(
        self, limit: int = 20, offset: int = 0
    ) -> tuple[List[Puzzle], int]:
        """List puzzles with pagination.

        Args:
            limit: Maximum number of puzzles to return
            offset: Number of puzzles to skip

        Returns:
            Tuple of (list of puzzles, total count)
        """

    @abstractmethod
    def store_solve(self, solve: SolverResult) -> SolverResult:
        """Store a solver result.

        Args:
            solve: The solver result to store

        Returns:
            The stored solver result
        """

    @abstractmethod
    def get_solve(self, solve_id: UUID) -> Optional[SolverResult]:
        """Retrieve a solver result by its ID.

        Args:
            solve_id: The unique identifier of the solver result

        Returns:
            The solver result if found, None otherwise
        """

    @abstractmethod
    def store_evaluation(self, evaluation: Evaluation) -> Evaluation:
        """Store an evaluation result.

        Args:
            evaluation: The evaluation to store

        Returns:
            The stored evaluation
        """

    @abstractmethod
    def get_evaluation(self, evaluation_id: UUID) -> Optional[Evaluation]:
        """Retrieve an evaluation by its ID.

        Args:
            evaluation_id: The unique identifier of the evaluation

        Returns:
            The evaluation if found, None otherwise
        """

    @abstractmethod
    def list_evaluations(
        self,
        solver_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[List[Evaluation], int]:
        """List evaluations with optional filtering and pagination.

        Args:
            solver_type: Optional filter by solver type
            limit: Maximum number of evaluations to return
            offset: Number of evaluations to skip

        Returns:
            Tuple of (list of evaluations, total count)
        """
