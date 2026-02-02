/**
 * @fileoverview Custom hook for puzzle operations with request cancellation
 * @module hooks/api/usePuzzle
 */

import { useRef } from 'react';
import { useMutation } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { createPuzzle as createPuzzleApi, getPuzzle } from '@/api/puzzles';
import { solvePuzzle as solvePuzzleApi } from '@/api/solvers';
import { evaluateSolve } from '@/api/evaluations';
import { createAbortController } from '@/api';
import { usePuzzleStore } from '@/stores/puzzleStore';
import type { CreatePuzzleRequest, SolverInfo, Puzzle } from '@/types/api';

/**
 * Custom hook for managing puzzle operations.
 *
 * Provides functions for creating puzzles, solving with different solvers,
 * and resetting application state. Automatically updates global puzzle store.
 *
 * **Request Cancellation:**
 * When a new puzzle is created or loaded while solvers are running,
 * all in-flight solver requests are automatically cancelled to prevent
 * wasted resources and outdated results.
 *
 * @returns Object containing puzzle operation functions
 *
 * @example
 * const { createPuzzle, solvePuzzle, solveWithAllSolvers, reset, cancelAll } = usePuzzle();
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
 * // Cancel all running solvers
 * cancelAll();
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

  // Store abort controllers for cancellation
  // Ref persists across renders without causing re-renders
  const solverAbortControllersRef = useRef<Map<string, AbortController>>(new Map());

  /**
   * Mutation for creating a new puzzle.
   * Automatically updates the global store with the created puzzle.
   */
  const createPuzzle = useMutation({
    mutationFn: async (data: CreatePuzzleRequest) => {
      const response = await createPuzzleApi(data);
      return response.data;
    },
    onSuccess: (puzzle: Puzzle) => {
      setPuzzle(puzzle);
    },
    onError: (error: Error) => {
      console.error('Failed to create puzzle:', error);
    },
  });

  /**
   * Cancels all running solver requests.
   *
   * **Use case:**
   * When user submits a new puzzle while solvers are running,
   * we cancel the old requests to avoid:
   * - Wasted backend resources
   * - Race conditions with outdated results
   * - Confusing UI states
   */
  const cancelAllSolvers = () => {
    solverAbortControllersRef.current.forEach((controller: AbortController, solverType: string) => {
      console.log(`Cancelling solver: ${solverType}`);
      controller.abort();
    });
    solverAbortControllersRef.current.clear();
  };

  /**
   * Solves a specific puzzle with a specific solver.
   * Automatically fetches evaluation after solving.
   * Supports cancellation via AbortController.
   *
   * @param puzzleId - ID of puzzle to solve
   * @param solverType - Name of solver to use (e.g., "random", "embedding")
   */
  const solvePuzzle = async (puzzleId: string, solverType: string) => {
    try {
      // Set loading state
      setSolverLoading(solverType, true);

      // Create abort controller for this solver
      const abortController = createAbortController();
      solverAbortControllersRef.current.set(solverType, abortController);

      // Execute solver with cancellation support
      const solveResponse = await solvePuzzleApi(
        puzzleId,
        solverType,
        undefined,
        { signal: abortController.signal }
      );
      const solverResult = solveResponse.data;

      // Update result
      setSolverResult(solverType, solverResult);

      // Fetch evaluation (also cancellable)
      const evalResponse = await evaluateSolve(solverResult.solve_id, {
        signal: abortController.signal,
      });
      const evaluation = evalResponse.data;

      // Update evaluation
      setSolverEvaluation(solverType, evaluation);

      // Remove controller after successful completion
      solverAbortControllersRef.current.delete(solverType);
    } catch (error: unknown) {
      // Handle cancellation gracefully - check for both Axios cancellation types
      if (
        (error instanceof Error && error.name === 'CanceledError') ||
        (error instanceof AxiosError && error.code === 'ERR_CANCELED')
      ) {
        console.log(`Solver ${solverType} was cancelled`);
        setSolverError(solverType, 'Cancelled');
      } else {
        const message = error instanceof Error ? error.message : 'Unknown error';
        setSolverError(solverType, message);
      }

      // Clean up controller
      solverAbortControllersRef.current.delete(solverType);
    } finally {
      // Always set loading to false
      setSolverLoading(solverType, false);
    }
  };

  /**
   * Solves a specific puzzle with all available solvers in parallel.
   * Uses Promise.allSettled to ensure all solvers complete even if some fail.
   * Cancels any previously running solvers before starting new ones.
   *
   * @param puzzleId - ID of puzzle to solve
   * @param solvers - Array of available solver information
   *
   * @example
   * const { data: solversData } = useSolvers();
   * if (solversData) {
   *   await solveWithAllSolvers(puzzleId, solversData.solvers);
   * }
   */
  const solveWithAllSolvers = async (puzzleId: string, solvers: SolverInfo[]) => {
    // Cancel any running solvers before starting new ones
    cancelAllSolvers();

    const promises = solvers.map((solver) => solvePuzzle(puzzleId, solver.solver_type));
    await Promise.allSettled(promises);
  };

  /**
   * Mutation for loading an existing puzzle by ID.
   * Fetches the puzzle from the backend and updates the global store.
   */
  const loadPuzzle = useMutation({
    mutationFn: async (puzzleId: string) => {
      const response = await getPuzzle(puzzleId);
      return response.data;
    },
    onSuccess: (puzzle: Puzzle) => {
      setPuzzle(puzzle);
    },
    onError: (error: Error) => {
      console.error('Failed to load puzzle:', error);
    },
  });

  /**
   * Loads a puzzle and solves it with all available solvers.
   *
   * @param puzzleId - ID of puzzle to load
   * @param solvers - Array of available solver information
   *
   * @example
   * await loadAndSolvePuzzle('puzzle-id-123', availableSolvers);
   */
  const loadAndSolvePuzzle = async (puzzleId: string, solvers: SolverInfo[]) => {
    try {
      await loadPuzzle.mutateAsync(puzzleId);
      await solveWithAllSolvers(puzzleId, solvers);
    } catch (error) {
      console.error('Failed to load and solve puzzle:', error);
      throw error;
    }
  };

  /**
   * Resets all puzzle state.
   * Clears current puzzle and all solver results.
   * Cancels any running solvers.
   */
  const reset = () => {
    cancelAllSolvers();
    resetStore();
  };

  return {
    createPuzzle,
    loadPuzzle,
    loadAndSolvePuzzle,
    solvePuzzle,
    solveWithAllSolvers,
    cancelAllSolvers,
    reset,
    currentPuzzle,
  };
};
