"""Tests for the evaluation comparator."""

import pytest
from connections_solver.evaluation.comparator import compare_solver_result
from connections_solver.core.models import (
    Puzzle,
    Solution,
    Category,
    SolverResult,
    PredictedCategory,
)


@pytest.fixture
def solution() -> Solution:
    """Create a test solution."""
    return Solution(
        categories=[
            Category(name="FISH", words=["BASS", "FLOUNDER", "SALMON", "TROUT"]),
            Category(name="SUITS", words=["DIAMOND", "HEART", "CLUB", "SPADE"]),
            Category(name="STATES", words=["MAINE", "OREGON", "OHIO", "UTAH"]),
            Category(name="BASES", words=["FIRST", "SECOND", "THIRD", "HOME"]),
        ]
    )


@pytest.fixture
def puzzle(solution: Solution) -> Puzzle:
    """Create a test puzzle."""
    return Puzzle(
        words=[
            "BASS", "FLOUNDER", "SALMON", "TROUT",
            "DIAMOND", "HEART", "CLUB", "SPADE",
            "MAINE", "OREGON", "OHIO", "UTAH",
            "FIRST", "SECOND", "THIRD", "HOME",
        ],
        solution=solution,
    )


def test_perfect_match(puzzle: Puzzle, solution: Solution) -> None:
    """Test evaluation with all categories exactly correct."""
    solver_result = SolverResult(
        puzzle_id=puzzle.puzzle_id,
        solver_type="test",
        execution_time_ms=100.0,
        predicted_categories=[
            PredictedCategory(words=["BASS", "FLOUNDER", "SALMON", "TROUT"]),
            PredictedCategory(words=["DIAMOND", "HEART", "CLUB", "SPADE"]),
            PredictedCategory(words=["MAINE", "OREGON", "OHIO", "UTAH"]),
            PredictedCategory(words=["FIRST", "SECOND", "THIRD", "HOME"]),
        ]
    )

    metrics = compare_solver_result(solver_result, solution)

    assert metrics.category_matches == 4
    assert metrics.accuracy == 1.0
    assert metrics.word_accuracy == 1.0
    assert metrics.exact_match is True


def test_partial_match(puzzle: Puzzle, solution: Solution) -> None:
    """Test evaluation with some categories correct."""
    solver_result = SolverResult(
        puzzle_id=puzzle.puzzle_id,
        solver_type="test",
        execution_time_ms=100.0,
        predicted_categories=[
            PredictedCategory(words=["BASS", "FLOUNDER", "SALMON", "TROUT"]),  # Correct
            PredictedCategory(words=["DIAMOND", "HEART", "CLUB", "SPADE"]),    # Correct
            PredictedCategory(words=["MAINE", "OREGON", "OHIO", "FIRST"]),     # Wrong
            PredictedCategory(words=["SECOND", "THIRD", "HOME", "UTAH"]),       # Wrong
        ]
    )

    metrics = compare_solver_result(solver_result, solution)

    assert metrics.category_matches == 2
    assert metrics.accuracy == 0.5
    assert metrics.word_accuracy == 0.875  # 14 out of 16 words correct (8 exact + 3 + 3)


def test_no_exact_matches(puzzle: Puzzle, solution: Solution) -> None:
    """Test evaluation with no exact matches but some correct words."""
    solver_result = SolverResult(
        puzzle_id=puzzle.puzzle_id,
        solver_type="test",
        execution_time_ms=100.0,
        predicted_categories=[
            PredictedCategory(words=["BASS", "FLOUNDER", "SALMON", "DIAMOND"]),  # 3 fish
            PredictedCategory(words=["TROUT", "HEART", "CLUB", "SPADE"]),        # 1 fish, 3 suits
            PredictedCategory(words=["MAINE", "OREGON", "OHIO", "FIRST"]),       # 3 states
            PredictedCategory(words=["UTAH", "SECOND", "THIRD", "HOME"]),         # 1 state, 3 bases
        ]
    )

    metrics = compare_solver_result(solver_result, solution)

    assert metrics.category_matches == 0
    assert metrics.accuracy == 0.0
    # Word accuracy should be 12/16 (3+3+3+3 with best match logic)
    assert metrics.word_accuracy == 0.75


def test_overlapping_categories_bug_fix(puzzle: Puzzle, solution: Solution) -> None:
    """Test that words aren't double-counted when a predicted category overlaps multiple true categories.

    This is the specific bug case mentioned in the plan:
    - Predicted: [A, B, C, D]
    - True1: [A, B, C, X]
    - True2: [A, B, D, Y]

    The fix ensures we only count the best match, not sum all overlaps.
    """
    solver_result = SolverResult(
        puzzle_id=puzzle.puzzle_id,
        solver_type="test",
        execution_time_ms=100.0,
        predicted_categories=[
            # This category overlaps with both FISH (3 words) and SUITS (1 word)
            # Should only count 3 (best match), not 3+1=4
            PredictedCategory(words=["BASS", "FLOUNDER", "SALMON", "DIAMOND"]),
            PredictedCategory(words=["HEART", "CLUB", "SPADE", "TROUT"]),
            PredictedCategory(words=["MAINE", "OREGON", "OHIO", "UTAH"]),      # Exact match
            PredictedCategory(words=["FIRST", "SECOND", "THIRD", "HOME"]),     # Exact match
        ]
    )

    metrics = compare_solver_result(solver_result, solution)

    # Should have 2 exact matches
    assert metrics.category_matches == 2

    # Word accuracy should not exceed 1.0 due to double counting
    assert metrics.word_accuracy <= 1.0

    # Should be exactly 14/16 = 0.875 (8 exact + 3 from first cat + 3 from second cat)
    assert metrics.word_accuracy == 0.875


def test_completely_wrong(puzzle: Puzzle, solution: Solution) -> None:
    """Test evaluation with all wrong groupings."""
    solver_result = SolverResult(
        puzzle_id=puzzle.puzzle_id,
        solver_type="test",
        execution_time_ms=100.0,
        predicted_categories=[
            PredictedCategory(words=["BASS", "DIAMOND", "MAINE", "FIRST"]),
            PredictedCategory(words=["FLOUNDER", "HEART", "OREGON", "SECOND"]),
            PredictedCategory(words=["SALMON", "CLUB", "OHIO", "THIRD"]),
            PredictedCategory(words=["TROUT", "SPADE", "UTAH", "HOME"]),
        ]
    )

    metrics = compare_solver_result(solver_result, solution)

    assert metrics.category_matches == 0
    assert metrics.accuracy == 0.0
    # Each predicted category has exactly 1 word from each true category
    # So word accuracy should be 4/16 = 0.25
    assert metrics.word_accuracy == 0.25
