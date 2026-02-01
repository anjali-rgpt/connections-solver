/**
 * @fileoverview Collapsible sidebar for puzzle creation
 * @module components/layout/Sidebar
 */

import React from 'react';
import { PuzzleForm } from './PuzzleForm';
import { PuzzleLoader } from './PuzzleLoader';
import type { SidebarProps } from './types';

/**
 * Sidebar Component
 *
 * Provides a collapsible right-side panel for puzzle management.
 * Contains a loader for existing puzzles and a form for creating new ones.
 *
 * Features:
 * - Load and solve existing puzzles
 * - Create new puzzles with validation
 * - Smooth slide-in/out animation
 * - Visible toggle button with arrow indicator
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
        {/* Load Existing Puzzle Section */}
        <section className="mb-8">
          <h2 className="text-xl font-bold mb-4 text-gray-800">
            Load Existing Puzzle
          </h2>
          <PuzzleLoader />
        </section>

        {/* Divider */}
        <div className="border-t-2 border-gray-200 my-8 relative">
          <span className="absolute left-1/2 -translate-x-1/2 -translate-y-1/2
            bg-white px-3 text-sm font-medium text-gray-500">
            OR
          </span>
        </div>

        {/* Create New Puzzle Section */}
        <section>
          <h2 className="text-xl font-bold mb-4 text-gray-800">
            Create New Puzzle
          </h2>
          <PuzzleForm />
        </section>
      </div>
    </div>
  );
};
