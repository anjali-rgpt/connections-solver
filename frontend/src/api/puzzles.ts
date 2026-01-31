/**
 * @fileoverview Puzzle-related API operations
 * @module api/puzzles
 */

import { apiClient } from './client';
import type { Puzzle, CreatePuzzleRequest } from '@/types/api';

/**
 * Creates a new puzzle with solution.
 *
 * @param data - Puzzle creation data (16 words + 4 categories)
 * @returns Promise resolving to created puzzle with ID
 *
 * @example
 * const puzzle = await createPuzzle({
 *   words: ['apple', 'banana', ...],
 *   solution: { categories: [...] }
 * });
 */
export const createPuzzle = (data: CreatePuzzleRequest) =>
  apiClient.post<Puzzle>('/puzzles', data);

/**
 * Retrieves a specific puzzle by ID.
 *
 * @param id - Puzzle UUID
 * @returns Promise resolving to puzzle data
 *
 * @example
 * const puzzle = await getPuzzle('123e4567-e89b-12d3-a456-426614174000');
 */
export const getPuzzle = (id: string) =>
  apiClient.get<Puzzle>(`/puzzles/${id}`);
