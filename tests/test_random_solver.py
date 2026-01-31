"""Tests for the random solver."""

import pytest
from connections_solver.solvers.random_solver import RandomSolver
from connections_solver.core.models import Puzzle


@pytest.fixture
def solver() -> RandomSolver:
    """Create a random solver instance."""
    return RandomSolver()


@pytest.fixture
def puzzle() -> Puzzle:
    """Create a test puzzle."""
    from connections_solver.core.models import Solution, Category

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


def test_correct_number_of_categories(solver: RandomSolver, puzzle: Puzzle) -> None:
    """Test that solver returns exactly 4 categories."""
    categories = solver.solve(puzzle.words)
    assert len(categories) == 4


def test_correct_words_per_category(solver: RandomSolver, puzzle: Puzzle) -> None:
    """Test that each category has exactly 4 words."""
    categories = solver.solve(puzzle.words)
    for category in categories:
        assert len(category.words) == 4


def test_all_words_used_once(solver: RandomSolver, puzzle: Puzzle) -> None:
    """Test that all 16 words are used exactly once."""
    categories = solver.solve(puzzle.words)

    all_words = []
    for category in categories:
        all_words.extend(category.words)

    # Check total count
    assert len(all_words) == 16

    # Check no duplicates
    assert len(set(all_words)) == 16

    # Check all original words present
    assert set(all_words) == set(puzzle.words)


def test_seed_reproducibility(puzzle: Puzzle) -> None:
    """Test that the same seed produces the same result."""
    solver1 = RandomSolver(config={"seed": 42})
    solver2 = RandomSolver(config={"seed": 42})

    result1 = solver1.solve(puzzle.words)
    result2 = solver2.solve(puzzle.words)

    # Convert to sets of frozensets for comparison (order doesn't matter)
    categories1 = [frozenset(cat.words) for cat in result1]
    categories2 = [frozenset(cat.words) for cat in result2]

    assert set(categories1) == set(categories2)


def test_different_seeds_produce_different_results(puzzle: Puzzle) -> None:
    """Test that different seeds likely produce different results."""
    solver1 = RandomSolver(config={"seed": 42})
    solver2 = RandomSolver(config={"seed": 123})

    result1 = solver1.solve(puzzle.words)
    result2 = solver2.solve(puzzle.words)

    # Convert to sets of frozensets
    categories1 = [frozenset(cat.words) for cat in result1]
    categories2 = [frozenset(cat.words) for cat in result2]

    # Very unlikely to be the same (though theoretically possible)
    assert set(categories1) != set(categories2)


def test_solver_registration(solver: RandomSolver) -> None:
    """Test that solver is properly registered."""
    from connections_solver.solvers.registry import SolverRegistry

    solvers = SolverRegistry.list_solvers()
    assert "random" in solvers
    assert solvers["random"] == RandomSolver
