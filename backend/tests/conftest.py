"""Pytest configuration and fixtures."""

import pytest
from connections_solver.core.models import Puzzle, Solution, Category
from connections_solver.storage.memory import MemoryStorage


@pytest.fixture
def sample_puzzle() -> Puzzle:
    """Create a sample puzzle for testing."""
    return Puzzle(
        puzzle_id="test-puzzle-1",
        words=[
            "BASS", "FLOUNDER", "SALMON", "TROUT",
            "DIAMOND", "HEART", "CLUB", "SPADE",
            "MAINE", "OREGON", "OHIO", "UTAH",
            "FIRST", "SECOND", "THIRD", "HOME",
        ],
    )


@pytest.fixture
def sample_solution() -> Solution:
    """Create a sample solution for testing."""
    return Solution(
        categories=[
            Category(
                name="FISH",
                words=["BASS", "FLOUNDER", "SALMON", "TROUT"],
            ),
            Category(
                name="PLAYING CARD SUITS",
                words=["DIAMOND", "HEART", "CLUB", "SPADE"],
            ),
            Category(
                name="U.S. STATES",
                words=["MAINE", "OREGON", "OHIO", "UTAH"],
            ),
            Category(
                name="BASEBALL BASES",
                words=["FIRST", "SECOND", "THIRD", "HOME"],
            ),
        ]
    )


@pytest.fixture
def storage() -> MemoryStorage:
    """Create a fresh storage instance for testing."""
    return MemoryStorage()
