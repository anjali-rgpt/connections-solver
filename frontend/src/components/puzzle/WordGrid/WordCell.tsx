/**
 * @fileoverview Individual word cell component
 * @module components/puzzle/WordGrid/WordCell
 */

import React from 'react';
import type { WordCellProps } from './types';

/**
 * WordCell Component
 *
 * Displays a single word in the grid with appropriate styling.
 * Color-coded based on category assignment.
 *
 * @param word - The word to display
 * @param colorClass - Tailwind CSS classes for background and border colors
 */
export const WordCell: React.FC<WordCellProps> = ({ word, colorClass }) => {
  return (
    <div
      className={`${colorClass} border-2 rounded-lg p-4 flex items-center
        justify-center text-center font-medium transition-colors duration-300
        min-h-[80px] text-sm sm:text-base uppercase tracking-wide`}
      role="gridcell"
    >
      {word}
    </div>
  );
};
