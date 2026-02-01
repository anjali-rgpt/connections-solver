/**
 * @fileoverview Evaluation-related API operations
 * @module api/evaluations
 */

import { apiClient } from './client';
import type { Evaluation } from '@/types/api';

/**
 * Evaluates a solver's performance on a puzzle.
 * Compares predicted categories against ground truth solution.
 *
 * @param solveId - UUID of solve attempt to evaluate
 * @param options - Optional Axios request options (including signal for cancellation)
 * @returns Promise resolving to evaluation metrics
 *
 * @example
 * const evaluation = await evaluateSolve('solve-uuid-here');
 * console.log(evaluation.data.metrics.accuracy); // 0.75
 *
 * @example
 * // With cancellation
 * const controller = new AbortController();
 * const evaluation = await evaluateSolve('solve-id', { signal: controller.signal });
 */
export const evaluateSolve = (solveId: string, options?: { signal?: AbortSignal }) =>
  apiClient.post<Evaluation>('/evaluate', { solve_id: solveId }, options);
