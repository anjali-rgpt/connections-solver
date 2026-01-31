/**
 * @fileoverview Type definitions for WordGrid module
 * @module components/puzzle/WordGrid/types
 */

import type { PredictedCategory } from '@/types/api';

/**
 * Props for WordGrid component.
 */
export interface WordGridProps {
  /** Array of exactly 16 words to display */
  words: string[];

  /** Optional solver predictions for color highlighting */
  predictedCategories?: PredictedCategory[];
}

/**
 * Props for WordCell component.
 */
export interface WordCellProps {
  /** The word to display */
  word: string;

  /** Tailwind CSS classes for styling */
  colorClass: string;
}
