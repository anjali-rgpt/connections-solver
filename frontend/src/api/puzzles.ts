/**
 * @fileoverview Puzzle-related API operations
 * @module api/puzzles
 */

import { apiClient } from './client';
import type { Puzzle, CreatePuzzleRequest, ListPuzzlesResponse } from '@/types/api';

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
 * Lists all available puzzles.
 *
 * @returns Promise resolving to paginated puzzle list
 *
 * @example
 * const response = await listPuzzles();
 * console.log(response.data.puzzles); // [{ puzzle_id: '...', words: [...], ... }, ...]
 * console.log(response.data.total); // Total number of puzzles
 */
export const listPuzzles = () =>
  apiClient.get<ListPuzzlesResponse>('/puzzles');

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

/**
 * Fetches a random puzzle from the wandb connections dataset.
 *
 * Returns a random NYT Connections puzzle from the external dataset
 * without storing it in the database. Each puzzle has 16 words and
 * 4 categories with difficulty levels (1-4).
 *
 * @returns Promise resolving to a random puzzle
 *
 * @example
 * const response = await getRandomPuzzle();
 * console.log(response.data.words); // ['nets', 'return', 'heat', ...]
 * console.log(response.data.solution.categories[0].difficulty); // 1 (Yellow/Easy)
 *
 * @throws {Error} If external source is unavailable (503) or data format is invalid (502)
 */
export const getRandomPuzzle = () =>
  apiClient.get<Puzzle>('/puzzles/random');
