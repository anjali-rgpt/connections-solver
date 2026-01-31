/**
 * @fileoverview Solver result display component
 * @module components/solver/SolverGrid
 */

import React, { useMemo } from 'react';
import { WordGrid } from '@/components/puzzle';
import { EvaluationScore } from '@/components/evaluation';
import { LoadingSpinner } from '@/components/common';
import { usePuzzleStore } from '@/stores/puzzleStore';
import { shuffleArray } from '@/utils/array';
import { formatExecutionTime } from '@/utils/formatting';
import type { SolverGridProps } from './types';

/**
 * SolverGrid Component
 *
 * Displays results for a single solver's attempt at solving the puzzle.
 * Shows:
 * - Solver name and description
 * - Loading spinner while solving
 * - Shuffled word grid with category colors
 * - Execution time
 * - Evaluation metrics
 * - Error message if failed
 *
 * @param solver - Solver information (name and description)
 *
 * @example
 * <SolverGrid solver={{ name: 'random', description: 'Random baseline solver' }} />
 */
export const SolverGrid: React.FC<SolverGridProps> = ({ solver }) => {
  const { currentPuzzle, solverStates } = usePuzzleStore();
  const solverState = solverStates[solver.name];

  // Shuffle words once when puzzle is set (stable across re-renders)
  const shuffledWords = useMemo(() => {
    if (!currentPuzzle) return [];
    return shuffleArray(currentPuzzle.words);
  }, [currentPuzzle]);

  if (!currentPuzzle) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
      {/* Header */}
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-gray-800">{solver.name}</h2>
        <p className="text-sm text-gray-600 mt-1">{solver.description}</p>
      </div>

      {/* Loading state */}
      {solverState?.isLoading && <LoadingSpinner />}

      {/* Error state */}
      {solverState?.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <p className="text-red-800 font-medium">Error</p>
          <p className="text-red-600 text-sm">{solverState.error}</p>
        </div>
      )}

      {/* Results */}
      {solverState?.result && (
        <>
          {/* Word grid with predictions */}
          <WordGrid
            words={shuffledWords}
            predictedCategories={solverState.result.predicted_categories}
          />

          {/* Execution time */}
          <div className="mt-4 text-center text-sm text-gray-600">
            Execution time:{' '}
            <span className="font-semibold">
              {formatExecutionTime(solverState.result.execution_time_ms)}
            </span>
          </div>

          {/* Evaluation metrics */}
          {solverState.evaluation && (
            <div className="mt-4">
              <EvaluationScore metrics={solverState.evaluation.metrics} />
            </div>
          )}
        </>
      )}

      {/* Empty state (no puzzle yet) */}
      {!solverState && (
        <div className="text-center text-gray-400 py-8">
          No puzzle loaded. Create a puzzle to see results.
        </div>
      )}
    </div>
  );
};
