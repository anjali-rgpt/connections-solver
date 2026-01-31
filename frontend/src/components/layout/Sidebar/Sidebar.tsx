/**
 * @fileoverview Collapsible sidebar for puzzle creation
 * @module components/layout/Sidebar
 */

import React from 'react';
import { PuzzleForm } from './PuzzleForm';
import type { SidebarProps } from './types';

/**
 * Sidebar Component
 *
 * Provides a collapsible right-side panel for creating new puzzles.
 * Contains a form for entering 4 categories with 4 words each.
 *
 * Features:
 * - Smooth slide-in/out animation
 * - Visible toggle button with arrow indicator
 * - Form validation before submission
 * - Reset functionality to clear all inputs
 *
 * @param isOpen - Controls sidebar visibility
 * @param onToggle - Callback when toggle button clicked
 *
 * @example
 * const [isOpen, setIsOpen] = useState(true);
 * <Sidebar isOpen={isOpen} onToggle={() => setIsOpen(!isOpen)} />
 */
export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle }) => {
  return (
    <div
      className={`fixed right-0 top-0 h-full bg-white shadow-2xl
        transition-transform duration-300 w-96 z-50
        ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}
    >
      {/* Toggle button */}
      <button
        onClick={onToggle}
        className="absolute left-0 top-1/2 -translate-x-full
          -translate-y-1/2 bg-blue-600 text-white p-3 rounded-l-lg
          shadow-lg hover:bg-blue-700 transition-colors"
        aria-label={isOpen ? 'Close sidebar' : 'Open sidebar'}
      >
        {isOpen ? '→' : '←'}
      </button>

      {/* Content */}
      <div className="h-full overflow-y-auto p-6">
        <h2 className="text-2xl font-bold mb-6">New Puzzle</h2>
        <PuzzleForm />
      </div>
    </div>
  );
};
