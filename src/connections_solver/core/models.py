"""Core domain models for the Connections Solver application."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Category(BaseModel):
    """Represents a category with 4 words and metadata.

    Attributes:
        name: The category name/theme (e.g., "FISH", "CARD SUITS")
        words: List of exactly 4 words belonging to this category
        difficulty: Optional difficulty level (1-4, where 1 is easiest)
    """

    name: str
    words: List[str] = Field(..., min_length=4, max_length=4)
    difficulty: Optional[int] = Field(None, ge=1, le=4)


class Solution(BaseModel):
    """Represents the complete solution to a puzzle.

    Attributes:
        categories: List of exactly 4 categories, each with 4 words
    """

    categories: List[Category] = Field(..., min_length=4, max_length=4)


class Puzzle(BaseModel):
    """Represents a Connections puzzle with 16 words and its solution.

    Attributes:
        puzzle_id: Unique identifier for the puzzle
        words: List of exactly 16 words to be grouped
        solution: The correct grouping of words into 4 categories
        metadata: Optional metadata (e.g., source, date, difficulty)
        created_at: Timestamp when the puzzle was created
    """

    puzzle_id: UUID = Field(default_factory=uuid4)
    words: List[str] = Field(..., min_length=16, max_length=16)
    solution: Solution
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PredictedCategory(BaseModel):
    """Represents a solver's predicted category grouping.

    Attributes:
        words: List of exactly 4 words grouped together
        confidence: Optional confidence score (0.0 to 1.0)
    """

    words: List[str] = Field(..., min_length=4, max_length=4)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class SolverResult(BaseModel):
    """Represents the result of a solver attempting to solve a puzzle.

    Attributes:
        solve_id: Unique identifier for this solve attempt
        puzzle_id: ID of the puzzle that was solved
        solver_type: Name of the solver used (e.g., "random", "embedding")
        predicted_categories: List of 4 predicted category groupings
        execution_time_ms: Time taken to solve in milliseconds
        solver_config: Optional configuration used by the solver
        solved_at: Timestamp when the puzzle was solved
    """

    solve_id: UUID = Field(default_factory=uuid4)
    puzzle_id: UUID
    solver_type: str
    predicted_categories: List[PredictedCategory] = Field(
        ..., min_length=4, max_length=4
    )
    execution_time_ms: float
    solver_config: Optional[Dict[str, Any]] = None
    solved_at: datetime = Field(default_factory=datetime.utcnow)


class CategoryEvaluation(BaseModel):
    """Evaluation metrics for a single category.

    Attributes:
        category_name: Name of the ground truth category
        precision: Precision score (0.0 to 1.0)
        recall: Recall score (0.0 to 1.0)
        f1: F1 score (0.0 to 1.0)
    """

    category_name: str
    precision: float = Field(..., ge=0.0, le=1.0)
    recall: float = Field(..., ge=0.0, le=1.0)
    f1: float = Field(..., ge=0.0, le=1.0)


class EvaluationMetrics(BaseModel):
    """Comprehensive evaluation metrics for a solver result.

    Attributes:
        accuracy: Category-level accuracy (proportion of exact matches)
        exact_match: Whether all 4 categories were perfectly matched
        category_matches: Number of categories that were exact matches
        total_categories: Total number of categories (always 4)
        word_accuracy: Proportion of words placed in correct category
        correctly_grouped_words: Number of words placed correctly
        total_words: Total number of words (always 16)
        per_category_scores: Detailed scores for each category
    """

    accuracy: float = Field(..., ge=0.0, le=1.0)
    exact_match: bool
    category_matches: int = Field(..., ge=0, le=4)
    total_categories: int = 4
    word_accuracy: float = Field(..., ge=0.0, le=1.0)
    correctly_grouped_words: int = Field(..., ge=0, le=16)
    total_words: int = 16
    per_category_scores: List[CategoryEvaluation]


class Evaluation(BaseModel):
    """Represents an evaluation of a solver result against ground truth.

    Attributes:
        evaluation_id: Unique identifier for this evaluation
        solve_id: ID of the solver result being evaluated
        puzzle_id: ID of the puzzle
        metrics: Computed evaluation metrics
        evaluated_at: Timestamp when the evaluation was performed
    """

    evaluation_id: UUID = Field(default_factory=uuid4)
    solve_id: UUID
    puzzle_id: UUID
    metrics: EvaluationMetrics
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
