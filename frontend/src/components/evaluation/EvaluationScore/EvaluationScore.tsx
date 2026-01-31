/**
 * @fileoverview Evaluation metrics display component
 * @module components/evaluation/EvaluationScore
 */

import React from 'react';
import { MetricCard } from './MetricCard';
import { CategoryScores } from './CategoryScores';
import { formatPercentage } from '@/utils/formatting';
import type { EvaluationScoreProps } from './types';

/**
 * EvaluationScore Component
 *
 * Displays comprehensive evaluation metrics for a solver's performance.
 * Shows main metrics in a grid and detailed per-category scores below.
 *
 * Main metrics:
 * - Accuracy: Overall word placement accuracy
 * - Word Accuracy: Fraction of words in correct categories
 * - Category Matches: Number of perfectly matched categories
 * - Exact Match: Whether all categories were perfect
 *
 * @param metrics - Evaluation metrics to display
 *
 * @example
 * <EvaluationScore metrics={evaluation.metrics} />
 */
export const EvaluationScore: React.FC<EvaluationScoreProps> = ({
  metrics,
}) => {
  return (
    <div className="p-4 bg-gray-50 rounded-lg">
      <h3 className="text-lg font-semibold mb-4">Evaluation Metrics</h3>

      {/* Main metrics grid */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <MetricCard
          label="Accuracy"
          value={formatPercentage(metrics.accuracy)}
          color={metrics.accuracy >= 0.75 ? 'success' : 'default'}
        />
        <MetricCard
          label="Word Accuracy"
          value={formatPercentage(metrics.word_accuracy)}
          color={metrics.word_accuracy >= 0.75 ? 'success' : 'default'}
        />
        <MetricCard
          label="Category Matches"
          value={`${metrics.category_matches}/4`}
          color={metrics.category_matches >= 3 ? 'success' : 'default'}
        />
        <MetricCard
          label="Exact Match"
          value={metrics.exact_match ? 'Yes' : 'No'}
          color={metrics.exact_match ? 'success' : 'default'}
        />
      </div>

      {/* Per-category scores */}
      <CategoryScores scores={metrics.per_category_scores} />
    </div>
  );
};
