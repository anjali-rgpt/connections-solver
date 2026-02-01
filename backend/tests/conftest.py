"""Pytest configuration and fixtures."""

import pytest
import numpy as np
from unittest.mock import patch
from connections_solver.core.models import Puzzle, Solution, Category
from connections_solver.storage.memory import MemoryStorage


@pytest.fixture
def sample_puzzle(sample_solution) -> Puzzle:
    """Create a sample puzzle for testing (without solution)."""
    return Puzzle(
        puzzle_id="test-puzzle-1",
        words=[
            "BASS", "FLOUNDER", "SALMON", "TROUT",
            "DIAMOND", "HEART", "CLUB", "SPADE",
            "MAINE", "OREGON", "OHIO", "UTAH",
            "FIRST", "SECOND", "THIRD", "HOME",
        ],
        solution=sample_solution,
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


@pytest.fixture
def mock_word2vec_model():
    """Mock Word2Vec model with deterministic embeddings.

    Avoids downloading the 1.6GB model in tests. Uses hash-based
    deterministic embeddings so tests are reproducible.
    """
    class MockModel:
        vector_size = 300

        def __getitem__(self, word):
            # Generate deterministic embedding based on word hash
            # Use modulo to keep seed within valid range
            seed = hash(word.lower()) % (2**32)
            np.random.seed(seed)
            return np.random.randn(300)

    return MockModel()


@pytest.fixture
def cluster_solver_with_mock(mock_word2vec_model):
    """ClusterSolver instance with mocked Word2Vec model.

    Patches the gensim API to return mock model instead of downloading.
    """
    from connections_solver.solvers.cluster_solver import ClusterSolver

    with patch('gensim.downloader.load') as mock_load:
        mock_load.return_value = mock_word2vec_model
        solver = ClusterSolver()
        yield solver
