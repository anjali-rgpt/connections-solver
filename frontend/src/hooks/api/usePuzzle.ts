/**
 * @fileoverview Custom hook for puzzle operations
 * @module hooks/api/usePuzzle
 */

import { useMutation } from '@tanstack/react-query';
import { createPuzzle as createPuzzleApi } from '@/api/puzzles';
import { solvePuzzle as solvePuzzleApi } from '@/api/solvers';
import { evaluateSolve } from '@/api/evaluations';
import { usePuzzleStore } from '@/stores/puzzleStore';
import type { CreatePuzzleRequest, SolverInfo } from '@/types/api';

/**
 * Custom hook for managing puzzle operations.
 *
 * Provides functions for creating puzzles, solving with different solvers,
 * and resetting application state. Automatically updates global puzzle store.
 *
 * @returns Object containing puzzle operation functions
 *
 * @example
 * const { createPuzzle, solvePuzzle, solveWithAllSolvers, reset } = usePuzzle();
 *
 * // Create a puzzle
 * await createPuzzle.mutateAsync({ words, solution });
 *
 * // Solve with one solver
 * await solvePuzzle('random');
 *
 * // Solve with all solvers in parallel
 * await solveWithAllSolvers(availableSolvers);
 *
 * // Reset state
 * reset();
 */
export const usePuzzle = () => {
  const {
    currentPuzzle,
    setPuzzle,
    setSolverLoading,
    setSolverResult,
    setSolverEvaluation,
    setSolverError,
    reset: resetStore,
  } = usePuzzleStore();

  /**
   * Mutation for creating a new puzzle.
   * Automatically updates the global store with the created puzzle.
   */
  const createPuzzle = useMutation({
    mutationFn: async (data: CreatePuzzleRequest) => {
      const response = await createPuzzleApi(data);
      return response.data;
    },
    onSuccess: (puzzle) => {
      setPuzzle(puzzle);
    },
    onError: (error) => {
      console.error('Failed to create puzzle:', error);
    },
  });

  /**
   * Solves the current puzzle with a specific solver.
   * Automatically fetches evaluation after solving.
   *
   * @param solverType - Name of solver to use (e.g., "random", "embedding")
   */
  const solvePuzzle = async (solverType: string) => {
    if (!currentPuzzle) {
      throw new Error('No puzzle loaded');
    }

    try {
      // Set loading state
      setSolverLoading(solverType, true);

      // Execute solver
      const solveResponse = await solvePuzzleApi(
        currentPuzzle.puzzle_id,
        solverType
      );
      const solverResult = solveResponse.data;

      // Update result
      setSolverResult(solverType, solverResult);

      // Fetch evaluation
      const evalResponse = await evaluateSolve(solverResult.solve_id);
      const evaluation = evalResponse.data;

      // Update evaluation
      setSolverEvaluation(solverType, evaluation);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      setSolverError(solverType, message);
    }
  };

  /**
   * Solves the current puzzle with all available solvers in parallel.
   * Uses Promise.allSettled to ensure all solvers complete even if some fail.
   *
   * @param solvers - Array of available solver information
   *
   * @example
   * const { data: solversData } = useSolvers();
   * if (solversData) {
   *   await solveWithAllSolvers(solversData.solvers);
   * }
   */
  const solveWithAllSolvers = async (solvers: SolverInfo[]) => {
    const promises = solvers.map((solver) => solvePuzzle(solver.name));
    await Promise.allSettled(promises);
  };

  /**
   * Resets all puzzle state.
   * Clears current puzzle and all solver results.
   */
  const reset = () => {
    resetStore();
  };

  return {
    createPuzzle,
    solvePuzzle,
    solveWithAllSolvers,
    reset,
    currentPuzzle,
  };
};
