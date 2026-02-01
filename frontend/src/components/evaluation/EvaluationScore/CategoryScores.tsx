/**
 * @fileoverview Per-category scores display component
 * @module components/evaluation/EvaluationScore/CategoryScores
 */

import React from 'react';
import { formatPercentage } from '@/utils/formatting';
import type { CategoryEvaluation } from '@/types/api';

interface CategoryScoresProps {
  scores: CategoryEvaluation[];
}

/**
 * CategoryScores Component
 *
 * Displays per-category precision, recall, and F1 scores in a table.
 *
 * @param scores - Array of category evaluation scores
 */
export const CategoryScores: React.FC<CategoryScoresProps> = ({ scores }) => {
  if (scores.length === 0) {
    return null;
  }

  return (
    <div className="mt-4">
      <h4 className="text-sm font-semibold text-gray-700 mb-2">
        Per-Category Scores
      </h4>
      <div className="space-y-2">
        {scores.map((score, index) => (
          <div
            key={index}
            className="bg-white border border-gray-200 rounded p-3"
          >
            <div className="font-medium text-sm mb-2">{score.category_name}</div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div>
                <span className="text-gray-600">Precision:</span>{' '}
                <span className="font-semibold">
                  {formatPercentage(score.precision)}
                </span>
              </div>
              <div>
                <span className="text-gray-600">Recall:</span>{' '}
                <span className="font-semibold">
                  {formatPercentage(score.recall)}
                </span>
              </div>
              <div>
                <span className="text-gray-600">F1:</span>{' '}
                <span className="font-semibold">
                  {formatPercentage(score.f1)}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
