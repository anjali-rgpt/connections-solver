/**
 * @fileoverview Grid display for puzzle words with category highlighting
 * @module components/puzzle/WordGrid
 */

import React from 'react';
import { WordCell } from './WordCell';
import { getCategoryColor, getWordCategory } from './utils';
import type { WordGridProps } from './types';

/**
 * WordGrid Component
 *
 * Displays a 4×4 grid of words with optional category-based color highlighting.
 * When solver results are provided, words are color-coded by their predicted category.
 *
 * Color scheme:
 * - Category 0: Yellow (bg-yellow-200)
 * - Category 1: Green (bg-green-200)
 * - Category 2: Blue (bg-blue-200)
 * - Category 3: Purple (bg-purple-200)
 *
 * @param words - Array of exactly 16 words to display
 * @param predictedCategories - Optional solver predictions for highlighting
 *
 * @example
 * // Without predictions (all gray)
 * <WordGrid words={puzzle.words} />
 *
 * @example
 * // With predictions (colored by category)
 * <WordGrid
 *   words={shuffledWords}
 *   predictedCategories={solverResult.predicted_categories}
 * />
 */
export const WordGrid: React.FC<WordGridProps> = ({
  words,
  predictedCategories,
}) => {
  if (words.length !== 16) {
    console.error('WordGrid requires exactly 16 words');
    return null;
  }

  return (
    <div
      className="grid grid-cols-4 gap-3 p-4"
      role="grid"
      aria-label="Puzzle word grid"
    >
      {words.map((word, index) => {
        const categoryIndex = getWordCategory(word, predictedCategories);
        const colorClass = getCategoryColor(categoryIndex);

        return (
          <WordCell
            key={`${word}-${index}`}
            word={word}
            colorClass={colorClass}
          />
        );
      })}
    </div>
  );
};
