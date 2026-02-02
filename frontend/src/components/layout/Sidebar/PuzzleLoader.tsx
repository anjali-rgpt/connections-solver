/**
 * @fileoverview Puzzle loader component for loading existing puzzles
 * @module components/layout/Sidebar/PuzzleLoader
 */

import React, { useState } from 'react';
import { usePuzzles } from '@/hooks/api/usePuzzles';
import { usePuzzle } from '@/hooks/api/usePuzzle';
import { useSolvers } from '@/hooks/api/useSolvers';
import { useToast } from '@/components/common';

/**
 * PuzzleLoader Component
 *
 * Allows users to select and load previously created puzzles.
 * Displays a dropdown of available puzzles with preview information.
 *
 * Features:
 * - Dropdown showing puzzle ID and preview words
 * - Load & Solve button to load puzzle and run all solvers
 * - Loading states and error handling
 * - Auto-refresh when new puzzles are created
 */
export const PuzzleLoader: React.FC = () => {
  const [selectedPuzzleId, setSelectedPuzzleId] = useState<string>('');
  const { data: puzzles, isLoading, error, refetch } = usePuzzles();
  const { data: solversData } = useSolvers();
  const { loadAndSolvePuzzle } = usePuzzle();
  const { success, error: showError } = useToast();

  const handleLoad = async () => {
    if (!selectedPuzzleId || !solversData?.solvers) return;

    try {
      await loadAndSolvePuzzle(selectedPuzzleId, solversData.solvers);
      success('Puzzle solved successfully with all solvers');
    } catch (error) {
      console.error('Failed to load puzzle:', error);
      showError('Failed to load puzzle. Please try again.');
    }
  };

  if (isLoading) {
    return (
      <div className="text-center py-4">
        <p className="text-sm text-gray-500">Loading puzzles...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
        <p className="text-yellow-800 text-sm font-medium">
          Unable to load puzzles
        </p>
        <p className="text-yellow-600 text-xs mt-1">
          {error instanceof Error ? error.message : 'Unknown error'}
        </p>
      </div>
    );
  }

  if (!puzzles || puzzles.length === 0) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <p className="text-blue-800 text-sm font-medium">No saved puzzles</p>
        <p className="text-blue-600 text-xs mt-1">
          Create a puzzle below to get started
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div>
        <label
          htmlFor="puzzle-select"
          className="block text-sm font-semibold text-gray-700 mb-2"
        >
          Select a Puzzle
        </label>
        <select
          id="puzzle-select"
          value={selectedPuzzleId}
          onChange={(e) => setSelectedPuzzleId(e.target.value)}
          className="w-full px-3 py-2 border-2 border-blue-300 rounded-lg
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            text-sm bg-white"
        >
          <option value="">-- Choose a puzzle --</option>
          {puzzles.map((puzzle) => (
            <option key={puzzle.puzzle_id} value={puzzle.puzzle_id}>
              {puzzle.puzzle_id.slice(0, 8)}... ({puzzle.words.slice(0, 3).join(', ')}...)
            </option>
          ))}
        </select>
      </div>

      <div className="flex gap-2">
        <button
          onClick={handleLoad}
          disabled={!selectedPuzzleId}
          className="flex-1 bg-green-600 text-white py-2 rounded-lg font-semibold
            hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed
            transition-colors text-sm"
        >
          Load & Solve
        </button>
        <button
          onClick={() => refetch()}
          className="px-3 bg-gray-200 text-gray-700 py-2 rounded-lg
            hover:bg-gray-300 transition-colors text-sm"
          title="Refresh puzzle list"
        >
          ↻
        </button>
      </div>

      {selectedPuzzleId && (
        <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
          <p>
            <span className="font-medium">Puzzle ID:</span>{' '}
            {selectedPuzzleId.slice(0, 16)}...
          </p>
        </div>
      )}
    </div>
  );
};
