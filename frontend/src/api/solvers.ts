/**
 * @fileoverview Solver-related API operations
 * @module api/solvers
 */

import { apiClient } from './client';
import type { SolverResult, ListSolversResponse, SolvePuzzleRequest } from '@/types/api';

/**
 * Lists all available solver types.
 *
 * @returns Promise resolving to array of solver information
 *
 * @example
 * const { data } = await listSolvers();
 * console.log(data.solvers); // [{ name: 'random', description: '...' }, ...]
 */
export const listSolvers = () =>
  apiClient.get<ListSolversResponse>('/solvers');

/**
 * Executes a solver on a specific puzzle.
 *
 * @param puzzleId - UUID of puzzle to solve
 * @param solverType - Name of solver (e.g., "random", "embedding")
 * @param config - Optional solver-specific configuration
 * @param options - Optional Axios request options (including signal for cancellation)
 * @returns Promise resolving to solver result with predictions
 *
 * @example
 * const result = await solvePuzzle(
 *   '123e4567-e89b-12d3-a456-426614174000',
 *   'random'
 * );
 *
 * @example
 * // With cancellation
 * const controller = new AbortController();
 * const result = await solvePuzzle(
 *   puzzleId,
 *   'random',
 *   undefined,
 *   { signal: controller.signal }
 * );
 */
export const solvePuzzle = (
  puzzleId: string,
  solverType: string,
  config?: Record<string, any>,
  options?: { signal?: AbortSignal }
) => {
  const request: SolvePuzzleRequest = {
    puzzle_id: puzzleId,
    solver_type: solverType,
    solver_config: config,
  };
  return apiClient.post<SolverResult>('/solve', request, options);
};
