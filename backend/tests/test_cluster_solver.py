"""Tests for the cluster solver."""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from connections_solver.solvers.cluster_solver import ClusterSolver
from connections_solver.core.models import Puzzle, Solution, Category


@pytest.fixture
def puzzle() -> Puzzle:
    """Create a test puzzle."""
    solution = Solution(
        categories=[
            Category(name="FISH", words=["BASS", "FLOUNDER", "SALMON", "TROUT"]),
            Category(name="SUITS", words=["DIAMOND", "HEART", "CLUB", "SPADE"]),
            Category(name="STATES", words=["MAINE", "OREGON", "OHIO", "UTAH"]),
            Category(name="BASES", words=["FIRST", "SECOND", "THIRD", "HOME"]),
        ]
    )

    return Puzzle(
        words=[
            "BASS", "FLOUNDER", "SALMON", "TROUT",
            "DIAMOND", "HEART", "CLUB", "SPADE",
            "MAINE", "OREGON", "OHIO", "UTAH",
            "FIRST", "SECOND", "THIRD", "HOME",
        ],
        solution=solution,
    )


# ===== Output Contract Tests =====

def test_correct_number_of_categories(cluster_solver_with_mock: ClusterSolver, puzzle: Puzzle) -> None:
    """Test that solver returns exactly 4 categories."""
    categories = cluster_solver_with_mock.solve(puzzle.words)
    assert len(categories) == 4


def test_correct_words_per_category(cluster_solver_with_mock: ClusterSolver, puzzle: Puzzle) -> None:
    """Test that each category has exactly 4 words."""
    categories = cluster_solver_with_mock.solve(puzzle.words)
    for category in categories:
        assert len(category.words) == 4


def test_all_words_used_once(cluster_solver_with_mock: ClusterSolver, puzzle: Puzzle) -> None:
    """Test that all 16 words are used exactly once."""
    categories = cluster_solver_with_mock.solve(puzzle.words)

    all_words = []
    for category in categories:
        all_words.extend(category.words)

    # Check total count
    assert len(all_words) == 16

    # Check no duplicates
    assert len(set(all_words)) == 16

    # Check all original words present
    assert set(all_words) == set(puzzle.words)


def test_confidence_scores_present(cluster_solver_with_mock: ClusterSolver, puzzle: Puzzle) -> None:
    """Test that each category has confidence score in [0, 1]."""
    categories = cluster_solver_with_mock.solve(puzzle.words)
    for category in categories:
        assert category.confidence is not None
        assert 0.0 <= category.confidence <= 1.0


# ===== Configuration Tests =====

def test_algorithm_override_kmeans(mock_word2vec_model, puzzle: Puzzle) -> None:
    """Test that config can force K-Means algorithm."""
    with patch('gensim.downloader.load') as mock_load:
        mock_load.return_value = mock_word2vec_model
        solver = ClusterSolver(config={"algorithm": "kmeans"})

        # Should not raise error and complete successfully
        categories = solver.solve(puzzle.words)
        assert len(categories) == 4


def test_algorithm_override_agglomerative(mock_word2vec_model, puzzle: Puzzle) -> None:
    """Test that config can force Agglomerative algorithm."""
    with patch('gensim.downloader.load') as mock_load:
        mock_load.return_value = mock_word2vec_model
        solver = ClusterSolver(config={"algorithm": "agglomerative"})

        categories = solver.solve(puzzle.words)
        assert len(categories) == 4


def test_algorithm_override_dbscan(mock_word2vec_model, puzzle: Puzzle) -> None:
    """Test that config can force DBSCAN algorithm."""
    with patch('gensim.downloader.load') as mock_load:
        mock_load.return_value = mock_word2vec_model
        solver = ClusterSolver(config={"algorithm": "dbscan"})

        categories = solver.solve(puzzle.words)
        assert len(categories) == 4


def test_default_algorithm(cluster_solver_with_mock: ClusterSolver, puzzle: Puzzle) -> None:
    """Test that no config uses auto-selection."""
    # Should not raise error - auto-selection should work
    categories = cluster_solver_with_mock.solve(puzzle.words)
    assert len(categories) == 4


def test_invalid_algorithm_raises_error(mock_word2vec_model, puzzle: Puzzle) -> None:
    """Test that invalid algorithm in config raises error."""
    with patch('gensim.downloader.load') as mock_load:
        mock_load.return_value = mock_word2vec_model
        solver = ClusterSolver(config={"algorithm": "invalid_algo"})

        with pytest.raises(ValueError):
            solver.solve(puzzle.words)


# ===== Metadata Tests =====

def test_metadata_structure(cluster_solver_with_mock: ClusterSolver, puzzle: Puzzle) -> None:
    """Test that SolverResult.solver_metadata has required keys."""
    result = cluster_solver_with_mock.solve_puzzle(puzzle)

    assert result.solver_metadata is not None
    assert "algorithm_selection" in result.solver_metadata
    assert "cluster_quality" in result.solver_metadata
    assert "visualization" in result.solver_metadata


def test_metadata_algorithm_selection(cluster_solver_with_mock: ClusterSolver, puzzle: Puzzle) -> None:
    """Test that metadata contains chosen algorithm and reason."""
    result = cluster_solver_with_mock.solve_puzzle(puzzle)

    algo_selection = result.solver_metadata["algorithm_selection"]
    assert "chosen" in algo_selection
    assert algo_selection["chosen"] in ["kmeans", "agglomerative", "dbscan"]
    assert "reason" in algo_selection
    assert isinstance(algo_selection["reason"], str)
    assert len(algo_selection["reason"]) > 0

    # Check metrics
    assert "metrics" in algo_selection
    assert "distance_cv" in algo_selection["metrics"]
    assert "pca_variance_2d" in algo_selection["metrics"]


def test_metadata_visualization_data(cluster_solver_with_mock: ClusterSolver, puzzle: Puzzle) -> None:
    """Test that metadata contains 16 coordinate points."""
    result = cluster_solver_with_mock.solve_puzzle(puzzle)

    viz = result.solver_metadata["visualization"]
    assert viz["method"] == "tsne"
    assert len(viz["coordinates_2d"]) == 16

    # Check structure of first point
    point = viz["coordinates_2d"][0]
    assert "word" in point
    assert "x" in point
    assert "y" in point
    assert "cluster" in point
    assert 0 <= point["cluster"] <= 3


def test_metadata_cluster_quality(cluster_solver_with_mock: ClusterSolver, puzzle: Puzzle) -> None:
    """Test that metadata contains confidence scores."""
    result = cluster_solver_with_mock.solve_puzzle(puzzle)

    quality = result.solver_metadata["cluster_quality"]
    assert "avg_confidence" in quality
    assert 0.0 <= quality["avg_confidence"] <= 1.0

    assert "confidence_per_cluster" in quality
    assert len(quality["confidence_per_cluster"]) == 4
    for conf in quality["confidence_per_cluster"]:
        assert 0.0 <= conf <= 1.0

    assert "distance_metrics" in quality
    metrics = quality["distance_metrics"]
    assert "euclidean_mean" in metrics
    assert "euclidean_std" in metrics
    assert "cosine_mean" in metrics
    assert "cosine_std" in metrics


def test_outlier_detection(cluster_solver_with_mock: ClusterSolver, puzzle: Puzzle) -> None:
    """Test that outliers array is valid (indices 0-15)."""
    result = cluster_solver_with_mock.solve_puzzle(puzzle)

    outliers = result.solver_metadata["visualization"]["outliers"]
    assert isinstance(outliers, list)
    for idx in outliers:
        assert 0 <= idx <= 15


# ===== Integration Tests =====

def test_solver_registration(cluster_solver_with_mock: ClusterSolver) -> None:
    """Test that 'cluster' is registered in SolverRegistry."""
    from connections_solver.solvers.registry import SolverRegistry

    solvers = SolverRegistry.list_solvers()
    assert "cluster" in solvers
    assert solvers["cluster"] == ClusterSolver


def test_with_example_puzzle(cluster_solver_with_mock: ClusterSolver, puzzle: Puzzle) -> None:
    """Test that solver can solve real puzzle end-to-end."""
    result = cluster_solver_with_mock.solve_puzzle(puzzle)

    # Check basic result structure
    assert result.puzzle_id == puzzle.puzzle_id
    assert result.solver_type == "Cluster Solver"
    assert len(result.predicted_categories) == 4
    assert result.execution_time_ms > 0
    assert result.solver_metadata is not None


def test_metadata_name_description_schema(cluster_solver_with_mock: ClusterSolver) -> None:
    """Test get_name(), get_description(), get_config_schema()."""
    assert cluster_solver_with_mock.get_name() == "Cluster Solver"

    description = cluster_solver_with_mock.get_description()
    assert isinstance(description, str)
    assert len(description) > 0

    schema = cluster_solver_with_mock.get_config_schema()
    assert "algorithm" in schema
    assert schema["algorithm"]["type"] == "string"
    assert "enum" in schema["algorithm"]


# ===== Caching Tests =====

def test_model_cache_reuse(mock_word2vec_model, puzzle: Puzzle) -> None:
    """Test that second instance doesn't reload model."""
    from connections_solver.solvers.embeddings.word2vec import Word2VecEmbeddingProvider

    # Clear cache first to ensure clean state
    Word2VecEmbeddingProvider.clear_cache()

    with patch('gensim.downloader.load') as mock_load:
        mock_load.return_value = mock_word2vec_model

        # First instance - should load model
        solver1 = ClusterSolver()
        assert mock_load.call_count == 1

        # Second instance - should reuse cache
        solver2 = ClusterSolver()
        # Still only 1 call (cached)
        assert mock_load.call_count == 1

        # Both should work
        categories1 = solver1.solve(puzzle.words)
        categories2 = solver2.solve(puzzle.words)
        assert len(categories1) == 4
        assert len(categories2) == 4


def test_cache_clear(mock_word2vec_model, puzzle: Puzzle) -> None:
    """Test that clear_cache() removes from global cache."""
    from connections_solver.solvers.embeddings.word2vec import Word2VecEmbeddingProvider

    # Clear cache first to ensure clean state
    Word2VecEmbeddingProvider.clear_cache()

    with patch('gensim.downloader.load') as mock_load:
        mock_load.return_value = mock_word2vec_model

        # Load once
        provider1 = Word2VecEmbeddingProvider()
        assert mock_load.call_count == 1

        # Clear cache
        Word2VecEmbeddingProvider.clear_cache()

        # Load again - should call API again
        provider2 = Word2VecEmbeddingProvider()
        assert mock_load.call_count == 2


def test_no_cache_option(mock_word2vec_model, puzzle: Puzzle) -> None:
    """Test that use_cache=False bypasses cache."""
    from connections_solver.solvers.embeddings.word2vec import Word2VecEmbeddingProvider

    with patch('gensim.downloader.load') as mock_load:
        mock_load.return_value = mock_word2vec_model

        # Load with no cache
        provider1 = Word2VecEmbeddingProvider(use_cache=False)
        assert mock_load.call_count == 1

        # Load again with no cache - should call API again
        provider2 = Word2VecEmbeddingProvider(use_cache=False)
        assert mock_load.call_count == 2


# ===== Edge Cases =====

def test_unknown_words(cluster_solver_with_mock: ClusterSolver) -> None:
    """Test handling of words not in vocabulary (uses zero vectors)."""
    # Create puzzle with nonsense words
    unknown_words = [
        "XYZABC1", "XYZABC2", "XYZABC3", "XYZABC4",
        "QWERTY1", "QWERTY2", "QWERTY3", "QWERTY4",
        "ASDFGH1", "ASDFGH2", "ASDFGH3", "ASDFGH4",
        "ZXCVBN1", "ZXCVBN2", "ZXCVBN3", "ZXCVBN4",
    ]

    # Should not crash - returns 4 categories with 4 words each
    categories = cluster_solver_with_mock.solve(unknown_words)
    assert len(categories) == 4
    for cat in categories:
        assert len(cat.words) == 4


def test_all_identical_embeddings(mock_word2vec_model, puzzle: Puzzle) -> None:
    """Test handling of degenerate case (all identical embeddings)."""
    # Create mock that returns same embedding for all words
    class IdenticalEmbeddingModel:
        vector_size = 300

        def __getitem__(self, word):
            # Always return same vector
            return np.ones(300)

    with patch('gensim.downloader.load') as mock_load:
        mock_load.return_value = IdenticalEmbeddingModel()
        solver = ClusterSolver()

        # Should handle gracefully (even if results are arbitrary)
        categories = solver.solve(puzzle.words)
        assert len(categories) == 4
        for cat in categories:
            assert len(cat.words) == 4
