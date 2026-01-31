"""Unit tests for storage implementations."""

import os
import tempfile
from datetime import datetime
from uuid import uuid4

import pytest

from src.connections_solver.core.models import (
    Puzzle,
    Solution,
    Category,
    SolverResult,
    PredictedCategory,
    Evaluation,
    EvaluationMetrics,
    CategoryEvaluation,
)
from src.connections_solver.storage.memory import MemoryStorage
from src.connections_solver.storage.sqlite import SQLiteStorage


# Test fixtures
@pytest.fixture
def sample_puzzle():
    """Create a sample puzzle for testing."""
    return Puzzle(
        puzzle_id=uuid4(),
        words=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"],
        solution=Solution(
            categories=[
                Category(name="Category1", words=["A", "B", "C", "D"], difficulty=1),
                Category(name="Category2", words=["E", "F", "G", "H"], difficulty=2),
                Category(name="Category3", words=["I", "J", "K", "L"], difficulty=3),
                Category(name="Category4", words=["M", "N", "O", "P"], difficulty=4),
            ]
        ),
        metadata={"source": "test", "date": "2024-01-01"},
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_solver_result(sample_puzzle):
    """Create a sample solver result for testing."""
    return SolverResult(
        solve_id=uuid4(),
        puzzle_id=sample_puzzle.puzzle_id,
        solver_type="random",
        predicted_categories=[
            PredictedCategory(words=["A", "B", "C", "D"], confidence=0.25),
            PredictedCategory(words=["E", "F", "G", "H"], confidence=0.25),
            PredictedCategory(words=["I", "J", "K", "L"], confidence=0.25),
            PredictedCategory(words=["M", "N", "O", "P"], confidence=0.25),
        ],
        execution_time_ms=100.0,
        solver_config={"seed": 42},
        solved_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_evaluation(sample_puzzle, sample_solver_result):
    """Create a sample evaluation for testing."""
    return Evaluation(
        evaluation_id=uuid4(),
        solve_id=sample_solver_result.solve_id,
        puzzle_id=sample_puzzle.puzzle_id,
        metrics=EvaluationMetrics(
            accuracy=1.0,
            exact_match=True,
            category_matches=4,
            total_categories=4,
            word_accuracy=1.0,
            correctly_grouped_words=16,
            total_words=16,
            per_category_scores=[
                CategoryEvaluation(category_name="Category1", precision=1.0, recall=1.0, f1=1.0),
                CategoryEvaluation(category_name="Category2", precision=1.0, recall=1.0, f1=1.0),
                CategoryEvaluation(category_name="Category3", precision=1.0, recall=1.0, f1=1.0),
                CategoryEvaluation(category_name="Category4", precision=1.0, recall=1.0, f1=1.0),
            ],
        ),
        evaluated_at=datetime.utcnow(),
    )


@pytest.fixture
def memory_storage():
    """Create a memory storage instance."""
    return MemoryStorage()


@pytest.fixture
def sqlite_storage():
    """Create a SQLite storage instance with a temporary database."""
    # Create a temporary file for the database
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    storage = SQLiteStorage(db_path=path)

    yield storage

    # Clean up
    if os.path.exists(path):
        os.remove(path)


# Tests for MemoryStorage
class TestMemoryStorage:
    """Test cases for MemoryStorage."""

    def test_store_and_get_puzzle(self, memory_storage, sample_puzzle):
        """Test storing and retrieving a puzzle."""
        stored = memory_storage.store_puzzle(sample_puzzle)
        assert stored.puzzle_id == sample_puzzle.puzzle_id

        retrieved = memory_storage.get_puzzle(sample_puzzle.puzzle_id)
        assert retrieved is not None
        assert retrieved.puzzle_id == sample_puzzle.puzzle_id
        assert retrieved.words == sample_puzzle.words
        assert len(retrieved.solution.categories) == 4

    def test_get_nonexistent_puzzle(self, memory_storage):
        """Test retrieving a puzzle that doesn't exist."""
        result = memory_storage.get_puzzle(uuid4())
        assert result is None

    def test_list_puzzles(self, memory_storage, sample_puzzle):
        """Test listing puzzles with pagination."""
        # Store multiple puzzles
        puzzle1 = memory_storage.store_puzzle(sample_puzzle)
        puzzle2 = Puzzle(
            puzzle_id=uuid4(),
            words=sample_puzzle.words,
            solution=sample_puzzle.solution,
        )
        memory_storage.store_puzzle(puzzle2)

        # List all puzzles
        puzzles, total = memory_storage.list_puzzles(limit=10)
        assert total == 2
        assert len(puzzles) == 2

        # Test pagination
        puzzles, total = memory_storage.list_puzzles(limit=1, offset=0)
        assert total == 2
        assert len(puzzles) == 1

    def test_store_and_get_solve(self, memory_storage, sample_solver_result):
        """Test storing and retrieving a solver result."""
        stored = memory_storage.store_solve(sample_solver_result)
        assert stored.solve_id == sample_solver_result.solve_id

        retrieved = memory_storage.get_solve(sample_solver_result.solve_id)
        assert retrieved is not None
        assert retrieved.solve_id == sample_solver_result.solve_id
        assert retrieved.solver_type == "random"

    def test_store_and_get_evaluation(self, memory_storage, sample_evaluation):
        """Test storing and retrieving an evaluation."""
        stored = memory_storage.store_evaluation(sample_evaluation)
        assert stored.evaluation_id == sample_evaluation.evaluation_id

        retrieved = memory_storage.get_evaluation(sample_evaluation.evaluation_id)
        assert retrieved is not None
        assert retrieved.evaluation_id == sample_evaluation.evaluation_id
        assert retrieved.metrics.accuracy == 1.0

    def test_list_evaluations_with_filter(
        self, memory_storage, sample_puzzle, sample_solver_result, sample_evaluation
    ):
        """Test listing evaluations with solver type filter."""
        # Store dependencies
        memory_storage.store_puzzle(sample_puzzle)
        memory_storage.store_solve(sample_solver_result)
        memory_storage.store_evaluation(sample_evaluation)

        # List evaluations for specific solver type
        evaluations, total = memory_storage.list_evaluations(solver_type="random")
        assert total == 1
        assert len(evaluations) == 1
        assert evaluations[0].evaluation_id == sample_evaluation.evaluation_id

        # List evaluations for non-existent solver type
        evaluations, total = memory_storage.list_evaluations(solver_type="nonexistent")
        assert total == 0
        assert len(evaluations) == 0


# Tests for SQLiteStorage
class TestSQLiteStorage:
    """Test cases for SQLiteStorage."""

    def test_store_and_get_puzzle(self, sqlite_storage, sample_puzzle):
        """Test storing and retrieving a puzzle."""
        stored = sqlite_storage.store_puzzle(sample_puzzle)
        assert stored.puzzle_id == sample_puzzle.puzzle_id

        retrieved = sqlite_storage.get_puzzle(sample_puzzle.puzzle_id)
        assert retrieved is not None
        assert str(retrieved.puzzle_id) == str(sample_puzzle.puzzle_id)
        assert retrieved.words == sample_puzzle.words
        assert len(retrieved.solution.categories) == 4
        assert retrieved.metadata == sample_puzzle.metadata

    def test_get_nonexistent_puzzle(self, sqlite_storage):
        """Test retrieving a puzzle that doesn't exist."""
        result = sqlite_storage.get_puzzle(uuid4())
        assert result is None

    def test_list_puzzles(self, sqlite_storage, sample_puzzle):
        """Test listing puzzles with pagination."""
        # Store multiple puzzles
        sqlite_storage.store_puzzle(sample_puzzle)
        puzzle2 = Puzzle(
            puzzle_id=uuid4(),
            words=sample_puzzle.words,
            solution=sample_puzzle.solution,
        )
        sqlite_storage.store_puzzle(puzzle2)

        # List all puzzles
        puzzles, total = sqlite_storage.list_puzzles(limit=10)
        assert total == 2
        assert len(puzzles) == 2

        # Test pagination
        puzzles, total = sqlite_storage.list_puzzles(limit=1, offset=0)
        assert total == 2
        assert len(puzzles) == 1

    def test_store_and_get_solve(self, sqlite_storage, sample_solver_result):
        """Test storing and retrieving a solver result."""
        stored = sqlite_storage.store_solve(sample_solver_result)
        assert stored.solve_id == sample_solver_result.solve_id

        retrieved = sqlite_storage.get_solve(sample_solver_result.solve_id)
        assert retrieved is not None
        assert str(retrieved.solve_id) == str(sample_solver_result.solve_id)
        assert retrieved.solver_type == "random"

    def test_store_and_get_evaluation(self, sqlite_storage, sample_evaluation):
        """Test storing and retrieving an evaluation."""
        stored = sqlite_storage.store_evaluation(sample_evaluation)
        assert stored.evaluation_id == sample_evaluation.evaluation_id

        retrieved = sqlite_storage.get_evaluation(sample_evaluation.evaluation_id)
        assert retrieved is not None
        assert str(retrieved.evaluation_id) == str(sample_evaluation.evaluation_id)
        assert retrieved.metrics.accuracy == 1.0

    def test_list_evaluations_with_filter(
        self, sqlite_storage, sample_puzzle, sample_solver_result, sample_evaluation
    ):
        """Test listing evaluations with solver type filter."""
        # Store dependencies
        sqlite_storage.store_puzzle(sample_puzzle)
        sqlite_storage.store_solve(sample_solver_result)
        sqlite_storage.store_evaluation(sample_evaluation)

        # List evaluations for specific solver type
        evaluations, total = sqlite_storage.list_evaluations(solver_type="random")
        assert total == 1
        assert len(evaluations) == 1

        # List evaluations for non-existent solver type
        evaluations, total = sqlite_storage.list_evaluations(solver_type="nonexistent")
        assert total == 0
        assert len(evaluations) == 0

    def test_persistence(self, sample_puzzle):
        """Test that data persists across storage instances."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        try:
            # Store puzzle in first instance
            storage1 = SQLiteStorage(db_path=path)
            storage1.store_puzzle(sample_puzzle)

            # Retrieve puzzle in second instance
            storage2 = SQLiteStorage(db_path=path)
            retrieved = storage2.get_puzzle(sample_puzzle.puzzle_id)

            assert retrieved is not None
            assert str(retrieved.puzzle_id) == str(sample_puzzle.puzzle_id)
        finally:
            if os.path.exists(path):
                os.remove(path)
