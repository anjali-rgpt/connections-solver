"""Wandb Connections dataset puzzle source implementation."""

import json
import random
from typing import Any, Dict, List

import httpx

from .base import BaseExternalPuzzleSource
from ..core.models import Puzzle, Solution, Category
from ..core.exceptions import ExternalPuzzleSourceError, PuzzleFormatError
from ..config import settings
from ..logging_config import get_logger

logger = get_logger(__name__)


class WandbConnectionsSource(BaseExternalPuzzleSource):
    """Fetch random puzzles from the wandb/connections GitHub dataset.

    This source fetches puzzles from a public JSONL file containing 353
    real NYT Connections puzzles. Each puzzle is converted from the wandb
    format to the application's Puzzle model with proper difficulty levels.

    Attributes:
        dataset_url: URL to the JSONL dataset
        timeout: HTTP request timeout in seconds
    """

    def __init__(
        self,
        dataset_url: str = None,
        timeout: int = None,
    ):
        """Initialize the wandb connections source.

        Args:
            dataset_url: URL to JSONL dataset (defaults to config setting)
            timeout: Request timeout in seconds (defaults to config setting)
        """
        self.dataset_url = dataset_url or settings.wandb_dataset_url
        self.timeout = timeout or settings.external_puzzle_timeout

    def fetch_random_puzzle(self) -> Puzzle:
        """Fetch a random puzzle from the wandb dataset.

        Returns:
            Puzzle instance with converted format and difficulty levels

        Raises:
            ExternalPuzzleSourceError: If HTTP request fails
            PuzzleFormatError: If puzzle data is invalid
        """
        logger.info(f"Fetching random puzzle from wandb dataset: {self.dataset_url}")

        try:
            # Fetch the dataset
            dataset_content = self._fetch_dataset()

            # Select a random puzzle
            puzzles = [line.strip() for line in dataset_content.split("\n") if line.strip()]
            if not puzzles:
                raise PuzzleFormatError("Dataset is empty")

            random_puzzle_json = random.choice(puzzles)
            logger.debug(f"Selected random puzzle from {len(puzzles)} available puzzles")

            # Parse and convert
            wandb_puzzle = json.loads(random_puzzle_json)
            puzzle = self._convert_wandb_to_puzzle(wandb_puzzle)

            logger.info(f"Successfully fetched random puzzle: puzzle_id={puzzle.puzzle_id}")
            return puzzle

        except httpx.HTTPError as exc:
            logger.error(f"HTTP error fetching wandb dataset: {exc}")
            raise ExternalPuzzleSourceError(
                f"Failed to fetch puzzle from external source: {exc}"
            ) from exc
        except json.JSONDecodeError as exc:
            logger.error(f"JSON decode error: {exc}")
            raise PuzzleFormatError(f"Invalid JSON in puzzle data: {exc}") from exc
        except KeyError as exc:
            logger.error(f"Missing required field in puzzle data: {exc}")
            raise PuzzleFormatError(f"Missing required field in puzzle: {exc}") from exc

    def _fetch_dataset(self) -> str:
        """Fetch the dataset content via HTTP.

        Returns:
            Raw dataset content as string

        Raises:
            httpx.HTTPError: If request fails
        """
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(self.dataset_url)
            response.raise_for_status()
            return response.text

    def _convert_wandb_to_puzzle(self, wandb_data: Dict[str, Any]) -> Puzzle:
        """Convert wandb puzzle format to application Puzzle model.

        The wandb format uses 'groups' with 'reason' fields, while our format
        uses 'categories' with 'name' fields. Categories are assigned difficulty
        levels based on their position (0=1, 1=2, 2=3, 3=4) following NYT standard.

        Args:
            wandb_data: Puzzle data in wandb format

        Returns:
            Puzzle instance in application format

        Raises:
            PuzzleFormatError: If data structure is invalid
        """
        try:
            # Extract words (should be 16)
            words = wandb_data["words"]
            if len(words) != 16:
                raise PuzzleFormatError(f"Expected 16 words, got {len(words)}")

            # Convert groups to categories with difficulty levels
            groups = wandb_data["solution"]["groups"]
            if len(groups) != 4:
                raise PuzzleFormatError(f"Expected 4 groups, got {len(groups)}")

            categories: List[Category] = []
            for idx, group in enumerate(groups):
                # Difficulty is 1-indexed based on position (Yellow=1, Green=2, Blue=3, Purple=4)
                difficulty = idx + 1

                category = Category(
                    name=group["reason"].upper(),  # Convert to uppercase for consistency
                    words=group["words"],
                    difficulty=difficulty,
                )
                categories.append(category)

            solution = Solution(categories=categories)

            # Create puzzle with metadata
            puzzle = Puzzle(
                words=words,
                solution=solution,
                metadata={
                    "source": "wandb/connections",
                    "dataset_url": self.dataset_url,
                },
            )

            return puzzle

        except (KeyError, TypeError, IndexError) as exc:
            raise PuzzleFormatError(f"Invalid wandb puzzle structure: {exc}") from exc
