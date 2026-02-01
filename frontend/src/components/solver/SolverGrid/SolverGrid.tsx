/**
 * @fileoverview Solver result display component
 * @module components/solver/SolverGrid
 */

import React, { useMemo } from 'react';
import { WordGrid } from '@/components/puzzle';
import { EvaluationScore } from '@/components/evaluation';
import { ProgressBar } from '@/components/common';
import { ClusterAnalysis } from '@/components/solver/ClusterAnalysis';
import { ClusterVisualization } from '@/components/solver/ClusterVisualization';
import { usePuzzleStore } from '@/stores/puzzleStore';
import { shuffleArray } from '@/utils/array';
import { formatExecutionTime, formatSolverName } from '@/utils/formatting';
import type { SolverGridProps } from './types';

/**
 * SolverGrid Component
 *
 * Displays results for a single solver's attempt at solving the puzzle.
 * Shows:
 * - Solver name (properly formatted) and description
 * - Progress bar while solving
 * - Shuffled word grid with category colors
 * - Execution time
 * - Collapsible evaluation metrics
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

  // Format solver name for display
  const formattedName = formatSolverName(solver.name);

  // Shuffle words once when puzzle is set (stable across re-renders)
  const shuffledWords = useMemo(() => {
    if (!currentPuzzle) return [];
    return shuffleArray(currentPuzzle.words);
  }, [currentPuzzle]);

  // Determine progress status message
  const getStatusMessage = () => {
    if (solverState?.isLoading) {
      if (solverState.result) {
        return 'Evaluating results';
      }
      return `Analyzing puzzle with ${formattedName} solver`;
    }
    return '';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">{formattedName}</h2>
        {solver.description && (
          <p className="text-sm text-gray-600">{solver.description}</p>
        )}
      </div>

      {/* No puzzle loaded state */}
      {!currentPuzzle && (
        <div className="text-center text-gray-500 py-12 px-4">
          <p className="text-lg font-medium mb-2">Ready to solve</p>
          <p className="text-sm">Create a puzzle using the sidebar to see this solver in action</p>
        </div>
      )}

      {/* Loading state */}
      {currentPuzzle && solverState?.isLoading && (
        <ProgressBar status={getStatusMessage()} />
      )}

      {/* Error state */}
      {currentPuzzle && solverState?.error && (
        <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-4">
          <p className="text-red-800 font-semibold mb-1">Solver Error</p>
          <p className="text-red-700 text-sm">{solverState.error}</p>
        </div>
      )}

      {/* Results */}
      {currentPuzzle && solverState?.result && (
        <>
          <div className="mb-4">
            <p className="text-sm font-medium text-gray-700 mb-2">
              Predicted Categories
            </p>
            <p className="text-xs text-gray-500 mb-3">
              Words are color-coded by the categories predicted by the {formattedName} solver
            </p>
          </div>

          {/* Word grid with predictions */}
          <WordGrid
            words={shuffledWords}
            predictedCategories={solverState.result.predicted_categories}
          />

          {/* Execution time */}
          <div className="mt-4 text-center">
            <span className="text-sm text-gray-600">Solved in </span>
            <span className="text-sm font-bold text-blue-600">
              {formatExecutionTime(solverState.result.execution_time_ms)}
            </span>
          </div>

          {/* Cluster solver explainability */}
          {solver.name === 'cluster' && solverState.result.solver_metadata && (
            <div className="mt-6">
              <ClusterAnalysis metadata={solverState.result.solver_metadata} />
              <ClusterVisualization metadata={solverState.result.solver_metadata} />
            </div>
          )}

          {/* Evaluation metrics */}
          {solverState.evaluation && (
            <div className="mt-6">
              <EvaluationScore metrics={solverState.evaluation.metrics} />
            </div>
          )}
        </>
      )}

      {/* Empty state after puzzle created but before solver runs */}
      {currentPuzzle && !solverState && (
        <div className="text-center text-gray-500 py-12 px-4">
          <div className="animate-pulse">
            <p className="text-lg font-medium mb-2">Initializing solver</p>
            <p className="text-sm">Preparing to analyze the puzzle...</p>
          </div>
        </div>
      )}
    </div>
  );
};
