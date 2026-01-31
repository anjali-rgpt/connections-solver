/**
 * @fileoverview API type definitions for MakingConnectionsAI
 * @module types/api
 */

/**
 * Represents a single category in a puzzle.
 * Each category contains 4 related words and optional difficulty rating.
 */
export interface Category {
  /** Display name for the category (e.g., "Types of Fish") */
  name: string;

  /** Array of exactly 4 words belonging to this category */
  words: string[];

  /** Optional difficulty level (1-4, where 4 is hardest) */
  difficulty?: number;
}

/**
 * The complete solution to a puzzle.
 * Contains exactly 4 categories, each with 4 words.
 */
export interface Solution {
  /** Array of exactly 4 categories */
  categories: Category[];
}

/**
 * Represents a puzzle with 16 words and solution categories.
 * Used as the primary data structure for puzzle creation and storage.
 */
export interface Puzzle {
  /** Unique identifier for the puzzle */
  puzzle_id: string;

  /** Array of exactly 16 words to be categorized */
  words: string[];

  /** The correct solution with 4 categories */
  solution: Solution;

  /** Optional metadata (source, date, difficulty, etc.) */
  metadata?: Record<string, any>;

  /** Timestamp when puzzle was created */
  created_at: string;
}

/**
 * Request payload for creating a new puzzle.
 */
export interface CreatePuzzleRequest {
  /** Array of exactly 16 words */
  words: string[];

  /** The correct solution with 4 categories */
  solution: Solution;

  /** Optional metadata */
  metadata?: Record<string, any>;
}

/**
 * A category predicted by a solver.
 * May include confidence score depending on solver type.
 */
export interface PredictedCategory {
  /** Array of words grouped together by the solver */
  words: string[];

  /** Optional confidence score (0-1) for this grouping */
  confidence?: number;
}

/**
 * Result from running a solver on a puzzle.
 * Contains predictions, timing, and metadata.
 */
export interface SolverResult {
  /** Unique identifier for this solve attempt */
  solve_id: string;

  /** ID of the puzzle that was solved */
  puzzle_id: string;

  /** Type of solver used (e.g., "random", "embedding", "llm") */
  solver_type: string;

  /** Predicted category groupings from the solver */
  predicted_categories: PredictedCategory[];

  /** Time taken to solve in milliseconds */
  execution_time_ms: number;

  /** Timestamp when solve was performed */
  solved_at: string;
}

/**
 * Request payload for solving a puzzle.
 */
export interface SolvePuzzleRequest {
  /** ID of puzzle to solve */
  puzzle_id: string;

  /** Type of solver to use */
  solver_type: string;

  /** Optional solver-specific configuration */
  solver_config?: Record<string, any>;
}

/**
 * Evaluation metrics for a single category.
 * Measures how well the solver identified this specific category.
 */
export interface CategoryEvaluation {
  /** Name of the category being evaluated */
  category_name: string;

  /** Precision: What fraction of predicted words were correct? (0-1) */
  precision: number;

  /** Recall: What fraction of actual words were found? (0-1) */
  recall: number;

  /** F1 Score: Harmonic mean of precision and recall (0-1) */
  f1: number;
}

/**
 * Overall evaluation metrics for a solver's performance.
 * Compares predicted categories against ground truth solution.
 */
export interface EvaluationMetrics {
  /** Overall accuracy: fraction of words placed in correct categories (0-1) */
  accuracy: number;

  /** Whether all 4 categories were matched exactly */
  exact_match: boolean;

  /** Number of categories matched perfectly (0-4) */
  category_matches: number;

  /** Fraction of words correctly categorized (0-1) */
  word_accuracy: number;

  /** Per-category precision/recall/F1 scores */
  per_category_scores: CategoryEvaluation[];
}

/**
 * Complete evaluation of a solver's performance.
 * Links metrics back to specific solve attempt and puzzle.
 */
export interface Evaluation {
  /** Unique identifier for this evaluation */
  evaluation_id: string;

  /** ID of the solve attempt being evaluated */
  solve_id: string;

  /** ID of the puzzle that was solved */
  puzzle_id: string;

  /** Computed evaluation metrics */
  metrics: EvaluationMetrics;

  /** Timestamp when evaluation was performed */
  evaluated_at: string;
}

/**
 * Information about an available solver.
 * Used to populate solver selection UI.
 */
export interface SolverInfo {
  /** Solver identifier (e.g., "random", "embedding") */
  name: string;

  /** Human-readable description of how the solver works */
  description: string;
}

/**
 * Response from the /solvers endpoint.
 */
export interface ListSolversResponse {
  /** Array of available solver types */
  solvers: SolverInfo[];
}
