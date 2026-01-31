"""Random baseline solver for Connections puzzles."""

import random
from typing import List, Dict, Any

from connections_solver.solvers.base import BaseSolver
from connections_solver.solvers.registry import register_solver
from connections_solver.core.models import PredictedCategory


@register_solver("random")
class RandomSolver(BaseSolver):
    """Baseline solver that randomly groups words into categories.

    This solver provides a baseline for comparison. It randomly
    shuffles the 16 words and groups them into 4 categories of 4 words each.
    The expected accuracy is around 1/2520 for perfect match (very low).
    """

    def solve(self, words: List[str]) -> List[PredictedCategory]:
        """Randomly group 16 words into 4 categories of 4 words each.

        Args:
            words: List of exactly 16 words to group

        Returns:
            List of 4 PredictedCategory objects with random groupings

        Raises:
            ValueError: If words list doesn't contain exactly 16 words
        """
        if len(words) != 16:
            raise ValueError(f"Expected 16 words, got {len(words)}")

        # Shuffle words randomly
        shuffled = words.copy()
        seed = self.config.get("seed")
        if seed is not None:
            random.seed(seed)
        random.shuffle(shuffled)

        # Group into 4 categories of 4 words each
        categories = []
        for i in range(4):
            start_idx = i * 4
            end_idx = start_idx + 4
            categories.append(
                PredictedCategory(
                    words=shuffled[start_idx:end_idx],
                    confidence=0.25,  # Random guess confidence (1/4)
                )
            )

        return categories

    def get_name(self) -> str:
        """Return the solver name.

        Returns:
            "random"
        """
        return "random"

    def get_description(self) -> str:
        """Return a description of the solver.

        Returns:
            Human-readable description
        """
        return "Random baseline solver that shuffles and groups words randomly"

    def get_config_schema(self) -> Dict[str, Any]:
        """Return the configuration schema for this solver.

        Returns:
            Dictionary describing config parameters
        """
        return {
            "seed": {
                "type": "integer",
                "description": "Random seed for reproducibility",
                "optional": True,
            }
        }
