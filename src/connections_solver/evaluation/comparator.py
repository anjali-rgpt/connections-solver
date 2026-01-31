"""Comparator for evaluating solver results against ground truth."""

from typing import List, Set

from connections_solver.core.models import (
    Solution,
    SolverResult,
    EvaluationMetrics,
    Category,
    PredictedCategory,
)
from connections_solver.evaluation.metrics import (
    find_best_matching_category,
    evaluate_category_match,
    is_exact_category_match,
)


def compare_solver_result(
    solver_result: SolverResult, ground_truth: Solution
) -> EvaluationMetrics:
    """Compare solver predictions against ground truth solution.

    This function evaluates how well the solver's predictions match
    the actual solution. It uses a greedy matching algorithm to pair
    predicted categories with ground truth categories.

    Args:
        solver_result: The solver's predictions
        ground_truth: The correct solution

    Returns:
        EvaluationMetrics with comprehensive evaluation scores
    """
    predicted_categories = solver_result.predicted_categories
    true_categories = ground_truth.categories.copy()

    # Track which true categories have been matched
    matched_categories: List[Category] = []
    category_evaluations = []
    exact_matches = 0

    # Greedy matching: for each prediction, find best matching true category
    for predicted in predicted_categories:
        # Find best match among remaining true categories
        remaining_true = [c for c in true_categories if c not in matched_categories]

        if remaining_true:
            best_match, _ = find_best_matching_category(predicted, remaining_true)
            matched_categories.append(best_match)

            # Evaluate this pairing
            category_eval = evaluate_category_match(predicted, best_match)
            category_evaluations.append(category_eval)

            # Check if it's an exact match
            if is_exact_category_match(predicted, best_match):
                exact_matches += 1

    # Calculate category-level accuracy
    category_accuracy = exact_matches / 4.0  # Always 4 categories

    # Calculate word-level accuracy
    correctly_grouped_words = _count_correctly_grouped_words(
        predicted_categories, true_categories
    )
    word_accuracy = correctly_grouped_words / 16.0  # Always 16 words

    return EvaluationMetrics(
        accuracy=category_accuracy,
        exact_match=(exact_matches == 4),
        category_matches=exact_matches,
        word_accuracy=word_accuracy,
        correctly_grouped_words=correctly_grouped_words,
        per_category_scores=category_evaluations,
    )


def _count_correctly_grouped_words(
    predicted_categories: List[PredictedCategory],
    true_categories: List[Category],
) -> int:
    """Count how many words are placed in their correct category.

    A word is considered correctly grouped if it appears in a predicted
    category that exactly matches one of the ground truth categories.

    Args:
        predicted_categories: List of predicted categories
        true_categories: List of ground truth categories

    Returns:
        Number of correctly grouped words
    """
    # Convert true categories to sets for efficient lookup
    true_category_sets: List[Set[str]] = [
        set(category.words) for category in true_categories
    ]

    correctly_grouped = 0

    for predicted in predicted_categories:
        predicted_set = set(predicted.words)

        # Check if this predicted category exactly matches a true category
        for true_set in true_category_sets:
            if predicted_set == true_set:
                correctly_grouped += 4  # All 4 words are correct
                break
        else:
            # No exact match - count individual correct words
            # A word is correct if it appears in the same category as other words
            # that are also in the same true category
            for true_set in true_category_sets:
                words_in_both = predicted_set & true_set
                # Only count if at least 1 word from true category is in prediction
                if words_in_both:
                    correctly_grouped += len(words_in_both)

    return min(correctly_grouped, 16)  # Cap at 16 words
