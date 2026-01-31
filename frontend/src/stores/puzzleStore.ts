/**
 * @fileoverview Global puzzle state management with Zustand
 * @module stores/puzzleStore
 */

import { create } from 'zustand';
import type { Puzzle, SolverResult, Evaluation } from '@/types/api';

/**
 * State for a single solver's execution.
 * Tracks loading, results, evaluation, and errors.
 */
interface SolverState {
  /** Solver result with predictions (undefined if not yet completed) */
  result?: SolverResult;

  /** Evaluation metrics (undefined if not yet evaluated) */
  evaluation?: Evaluation;

  /** Whether this solver is currently running */
  isLoading: boolean;

  /** Error message if solver failed */
  error?: string;
}

/**
 * Global puzzle store state.
 * Manages current puzzle and all solver states.
 */
interface PuzzleStore {
  /** Currently active puzzle (undefined if none created) */
  currentPuzzle?: Puzzle;

  /** Map of solver type -> solver state */
  solverStates: Record<string, SolverState>;

  /**
   * Sets the current puzzle.
   * Resets all solver states when new puzzle is set.
   *
   * @param puzzle - The puzzle to set as current
   */
  setPuzzle: (puzzle: Puzzle) => void;

  /**
   * Updates loading state for a specific solver.
   *
   * @param solverType - Name of the solver
   * @param loading - Whether the solver is loading
   */
  setSolverLoading: (solverType: string, loading: boolean) => void;

  /**
   * Sets the result for a specific solver.
   * Automatically sets loading to false.
   *
   * @param solverType - Name of the solver
   * @param result - Solver result with predictions
   */
  setSolverResult: (solverType: string, result: SolverResult) => void;

  /**
   * Sets the evaluation for a specific solver.
   *
   * @param solverType - Name of the solver
   * @param evaluation - Evaluation metrics
   */
  setSolverEvaluation: (solverType: string, evaluation: Evaluation) => void;

  /**
   * Sets an error for a specific solver.
   * Automatically sets loading to false.
   *
   * @param solverType - Name of the solver
   * @param error - Error message
   */
  setSolverError: (solverType: string, error: string) => void;

  /**
   * Resets all state to initial values.
   * Clears current puzzle and all solver states.
   */
  reset: () => void;
}

/**
 * Global puzzle store.
 * Use this hook to access and update puzzle state from any component.
 *
 * @example
 * const { currentPuzzle, solverStates, setPuzzle } = usePuzzleStore();
 */
export const usePuzzleStore = create<PuzzleStore>((set) => ({
  currentPuzzle: undefined,
  solverStates: {},

  setPuzzle: (puzzle) =>
    set({
      currentPuzzle: puzzle,
      solverStates: {}, // Reset solver states when new puzzle is set
    }),

  setSolverLoading: (solverType, loading) =>
    set((state) => ({
      solverStates: {
        ...state.solverStates,
        [solverType]: {
          ...state.solverStates[solverType],
          isLoading: loading,
        },
      },
    })),

  setSolverResult: (solverType, result) =>
    set((state) => ({
      solverStates: {
        ...state.solverStates,
        [solverType]: {
          ...state.solverStates[solverType],
          result,
          isLoading: false,
          error: undefined,
        },
      },
    })),

  setSolverEvaluation: (solverType, evaluation) =>
    set((state) => ({
      solverStates: {
        ...state.solverStates,
        [solverType]: {
          ...state.solverStates[solverType],
          evaluation,
        },
      },
    })),

  setSolverError: (solverType, error) =>
    set((state) => ({
      solverStates: {
        ...state.solverStates,
        [solverType]: {
          ...state.solverStates[solverType],
          isLoading: false,
          error,
        },
      },
    })),

  reset: () =>
    set({
      currentPuzzle: undefined,
      solverStates: {},
    }),
}));
