/**
 * @fileoverview Evaluation metrics display component
 * @module components/evaluation/EvaluationScore
 */

import React, { useState } from 'react';
import { MetricCard } from './MetricCard';
import { CategoryScores } from './CategoryScores';
import { formatPercentage } from '@/utils/formatting';
import type { EvaluationScoreProps } from './types';

/**
 * EvaluationScore Component
 *
 * Displays comprehensive evaluation metrics for a solver's performance.
 * Collapsible accordion-style component with expandable details.
 *
 * Main metrics (always visible when expanded):
 * - Accuracy: Overall word placement accuracy
 * - Word Accuracy: Fraction of words in correct categories
 * - Category Matches: Number of perfectly matched categories
 * - Exact Match: Whether all categories were perfect
 *
 * Per-category scores shown when expanded.
 *
 * @param metrics - Evaluation metrics to display
 *
 * @example
 * <EvaluationScore metrics={evaluation.metrics} />
 */
export const EvaluationScore: React.FC<EvaluationScoreProps> = ({
  metrics,
}) => {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="border-2 border-gray-200 rounded-lg overflow-hidden">
      {/* Collapsible Header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 bg-gradient-to-r from-blue-50 to-indigo-50
          hover:from-blue-100 hover:to-indigo-100 transition-colors
          flex items-center justify-between group"
      >
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-gray-800">
            Performance Metrics
          </span>
          <span className="text-xs font-medium text-gray-500 bg-white px-2 py-1 rounded">
            {formatPercentage(metrics.accuracy)} accurate
          </span>
        </div>
        <svg
          className={`w-5 h-5 text-gray-600 transition-transform duration-200
            ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {/* Collapsible Content */}
      {isOpen && (
        <div className="p-4 bg-gray-50">
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
      )}
    </div>
  );
};
