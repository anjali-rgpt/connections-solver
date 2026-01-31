"""In-memory storage implementation using Python dictionaries."""

from typing import Dict, List, Optional
from uuid import UUID

from connections_solver.core.models import Puzzle, SolverResult, Evaluation
from connections_solver.storage.base import BaseStorage


class MemoryStorage(BaseStorage):
    """In-memory storage implementation.

    This implementation stores all data in Python dictionaries.
    Data is lost when the application restarts.
    Suitable for development and testing.
    """

    def __init__(self) -> None:
        """Initialize empty storage dictionaries."""
        self._puzzles: Dict[UUID, Puzzle] = {}
        self._solves: Dict[UUID, SolverResult] = {}
        self._evaluations: Dict[UUID, Evaluation] = {}

    def store_puzzle(self, puzzle: Puzzle) -> Puzzle:
        """Store a puzzle in memory.

        Args:
            puzzle: The puzzle to store

        Returns:
            The stored puzzle
        """
        self._puzzles[puzzle.puzzle_id] = puzzle
        return puzzle

    def get_puzzle(self, puzzle_id: UUID) -> Optional[Puzzle]:
        """Retrieve a puzzle by its ID.

        Args:
            puzzle_id: The unique identifier of the puzzle

        Returns:
            The puzzle if found, None otherwise
        """
        return self._puzzles.get(puzzle_id)

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
        all_puzzles = list(self._puzzles.values())
        total = len(all_puzzles)

        # Sort by created_at descending (newest first)
        all_puzzles.sort(key=lambda p: p.created_at, reverse=True)

        # Apply pagination
        paginated = all_puzzles[offset : offset + limit]

        return paginated, total

    def store_solve(self, solve: SolverResult) -> SolverResult:
        """Store a solver result in memory.

        Args:
            solve: The solver result to store

        Returns:
            The stored solver result
        """
        self._solves[solve.solve_id] = solve
        return solve

    def get_solve(self, solve_id: UUID) -> Optional[SolverResult]:
        """Retrieve a solver result by its ID.

        Args:
            solve_id: The unique identifier of the solver result

        Returns:
            The solver result if found, None otherwise
        """
        return self._solves.get(solve_id)

    def store_evaluation(self, evaluation: Evaluation) -> Evaluation:
        """Store an evaluation result in memory.

        Args:
            evaluation: The evaluation to store

        Returns:
            The stored evaluation
        """
        self._evaluations[evaluation.evaluation_id] = evaluation
        return evaluation

    def get_evaluation(self, evaluation_id: UUID) -> Optional[Evaluation]:
        """Retrieve an evaluation by its ID.

        Args:
            evaluation_id: The unique identifier of the evaluation

        Returns:
            The evaluation if found, None otherwise
        """
        return self._evaluations.get(evaluation_id)

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
        all_evaluations = list(self._evaluations.values())

        # Filter by solver_type if specified
        if solver_type:
            # Get all solve_ids for the specified solver type
            relevant_solve_ids = {
                solve.solve_id
                for solve in self._solves.values()
                if solve.solver_type == solver_type
            }
            all_evaluations = [
                e for e in all_evaluations if e.solve_id in relevant_solve_ids
            ]

        total = len(all_evaluations)

        # Sort by evaluated_at descending (newest first)
        all_evaluations.sort(key=lambda e: e.evaluated_at, reverse=True)

        # Apply pagination
        paginated = all_evaluations[offset : offset + limit]

        return paginated, total
