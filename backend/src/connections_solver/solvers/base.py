"""Abstract base class for all solver implementations."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time

from ..core.models import Puzzle, SolverResult, PredictedCategory


class BaseSolver(ABC):
    """Abstract base class for all solver implementations.

    This class defines the interface that all solvers must implement.
    It provides common functionality like timing and result wrapping.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize solver with optional configuration.

        Args:
            config: Solver-specific configuration parameters
        """
        self.config = config or {}

    @abstractmethod
    def solve(self, words: List[str]) -> List[PredictedCategory]:
        """Solve the puzzle by grouping 16 words into 4 categories.

        This is the main method that subclasses must implement.
        It should return exactly 4 PredictedCategory objects,
        each containing exactly 4 words.

        Args:
            words: List of exactly 16 words to group

        Returns:
            List of 4 PredictedCategory objects

        Raises:
            ValueError: If words list doesn't contain exactly 16 words
        """

    def solve_puzzle(self, puzzle: Puzzle) -> SolverResult:
        """Solve a puzzle and return a complete result with metadata.

        This method wraps the solve() method to add timing and
        construct a complete SolverResult object.

        Args:
            puzzle: Puzzle object to solve

        Returns:
            SolverResult with predicted categories and execution time
        """
        start_time = time.time()
        predicted_categories = self.solve(puzzle.words)
        execution_time_ms = (time.time() - start_time) * 1000

        return SolverResult(
            puzzle_id=puzzle.puzzle_id,
            solver_type=self.get_name(),
            predicted_categories=predicted_categories,
            execution_time_ms=execution_time_ms,
            solver_config=self.config,
        )

    @abstractmethod
    def get_name(self) -> str:
        """Return the unique name/identifier of this solver.

        Returns:
            Solver name (e.g., "random", "embedding")
        """

    @abstractmethod
    def get_description(self) -> str:
        """Return a human-readable description of this solver.

        Returns:
            Solver description
        """

    @abstractmethod
    def get_config_schema(self) -> Dict[str, Any]:
        """Return JSON schema describing configuration options.

        Returns:
            Dictionary describing config parameters
        """
