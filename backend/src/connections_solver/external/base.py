"""Abstract base class for external puzzle sources."""

from abc import ABC, abstractmethod

from ..core.models import Puzzle


class BaseExternalPuzzleSource(ABC):
    """Abstract interface for external puzzle sources.

    This defines the contract that all external puzzle source implementations
    must follow. Implementations can fetch puzzles from various sources like
    public datasets, APIs, or other external services.
    """

    @abstractmethod
    def fetch_random_puzzle(self) -> Puzzle:
        """Fetch a random puzzle from the external source.

        Returns:
            A Puzzle instance with 16 words, solution, and metadata

        Raises:
            ExternalPuzzleSourceError: If fetching fails (network, timeout, etc.)
            PuzzleFormatError: If puzzle data has invalid format
        """
