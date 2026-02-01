"""Evaluation metrics for comparing solver results against ground truth."""

from typing import Set, List

from ..core.models import (
    Category,
    PredictedCategory,
    CategoryEvaluation,
)


def calculate_precision_recall_f1(
    predicted_words: Set[str], true_words: Set[str]
) -> tuple[float, float, float]:
    """Calculate precision, recall, and F1 score for a category.

    Args:
        predicted_words: Set of words in predicted category
        true_words: Set of words in ground truth category

    Returns:
        Tuple of (precision, recall, f1)
    """
    if not predicted_words:
        return 0.0, 0.0, 0.0

    true_positives = len(predicted_words & true_words)

    precision = true_positives / len(predicted_words) if predicted_words else 0.0
    recall = true_positives / len(true_words) if true_words else 0.0

    if precision + recall > 0:
        f1_score = 2 * (precision * recall) / (precision + recall)
    else:
        f1_score = 0.0

    return precision, recall, f1_score


def find_best_matching_category(
    predicted: PredictedCategory, true_categories: List[Category]
) -> tuple[Category, float]:
    """Find the best matching ground truth category for a prediction.

    Args:
        predicted: Predicted category
        true_categories: List of ground truth categories

    Returns:
        Tuple of (best matching category, F1 score)
    """
    best_category = true_categories[0]
    best_f1 = 0.0

    predicted_set = set(predicted.words)

    for true_category in true_categories:
        true_set = set(true_category.words)
        _, _, f1_score = calculate_precision_recall_f1(predicted_set, true_set)

        if f1_score > best_f1:
            best_f1 = f1_score
            best_category = true_category

    return best_category, best_f1


def evaluate_category_match(
    predicted: PredictedCategory, true_category: Category
) -> CategoryEvaluation:
    """Evaluate a predicted category against a ground truth category.

    Args:
        predicted: Predicted category
        true_category: Ground truth category

    Returns:
        CategoryEvaluation with precision, recall, and F1 scores
    """
    predicted_set = set(predicted.words)
    true_set = set(true_category.words)

    precision, recall, f1_score = calculate_precision_recall_f1(
        predicted_set, true_set
    )

    return CategoryEvaluation(
        category_name=true_category.name,
        precision=precision,
        recall=recall,
        f1=f1_score,
    )


def is_exact_category_match(
    predicted: PredictedCategory, true_category: Category
) -> bool:
    """Check if a predicted category exactly matches a ground truth category.

    Args:
        predicted: Predicted category
        true_category: Ground truth category

    Returns:
        True if all 4 words match exactly, False otherwise
    """
    return set(predicted.words) == set(true_category.words)
