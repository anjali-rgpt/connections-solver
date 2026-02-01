"""Embeddings + text clustering solver for Connections puzzles"""

from typing import List, Dict, Any

from .base import BaseSolver
from .registry import register_solver
from ..core.models import PredictedCategory

@register_solver("cluster")
class ClusterSolver(BaseSolver):
    """This solver converts the words into embeddings and then clusters them based on vector similarity using K-Means or other clustering techniques depending on the data properties. 
    It is meant to be a step-up from the random solver, as it takes into account how words may be related to each other based on their embeddings.
    """

    def solve(self, words: List[str]) -> List[PredictedCategory]:
        """Solve the puzzle by clustering the words into categories"""
        return []

    def get_name(self) -> str:
        """Return the name of the solver"""
        return "Cluster Solver"

    def get_description(self) -> str:
        """Return the description of the solver"""
        return "This solver converts the words into embeddings and then clusters them based on vector similarity using K-Means or other clustering techniques depending on the data properties. It is meant to be a step-up from the random solver, as it takes into account how words may be related to each other based on their embeddings."