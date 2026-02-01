/**
 * @fileoverview Utility functions for WordGrid component
 * @module components/puzzle/WordGrid/utils
 */

import type { PredictedCategory } from '@/types/api';

/** Category color mappings */
const CATEGORY_COLORS = [
  'bg-yellow-200 border-yellow-400',
  'bg-green-200 border-green-400',
  'bg-blue-200 border-blue-400',
  'bg-purple-200 border-purple-400',
] as const;

/**
 * Determines which category (if any) a word belongs to.
 *
 * @param word - The word to check
 * @param categories - Predicted categories from solver
 * @returns Category index (0-3) or null if not found
 */
export const getWordCategory = (
  word: string,
  categories?: PredictedCategory[]
): number | null => {
  if (!categories) return null;

  const index = categories.findIndex((cat) =>
    cat.words.includes(word)
  );

  return index >= 0 ? index : null;
};

/**
 * Gets the CSS color class for a category index.
 *
 * @param categoryIndex - Index from 0-3, or null for default
 * @returns Tailwind CSS class string
 */
export const getCategoryColor = (categoryIndex: number | null): string => {
  return categoryIndex !== null
    ? CATEGORY_COLORS[categoryIndex]
    : 'bg-gray-100 border-gray-300';
};
