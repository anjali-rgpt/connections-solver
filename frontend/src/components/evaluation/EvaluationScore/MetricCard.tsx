/**
 * @fileoverview Individual metric card component
 * @module components/evaluation/EvaluationScore/MetricCard
 */

import React from 'react';
import type { MetricCardProps } from './types';

/**
 * MetricCard Component
 *
 * Displays a single evaluation metric with label and value.
 *
 * @param label - Metric label (e.g., "Accuracy")
 * @param value - Formatted metric value (e.g., "75.0%")
 * @param color - Color scheme for the card
 */
export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  color = 'default',
}) => {
  const colorClasses = {
    default: 'bg-gray-50 border-gray-200',
    success: 'bg-green-50 border-green-200',
    warning: 'bg-yellow-50 border-yellow-200',
    error: 'bg-red-50 border-red-200',
  };

  return (
    <div
      className={`${colorClasses[color]} border-2 rounded-lg p-4 text-center`}
    >
      <div className="text-sm text-gray-600 mb-1">{label}</div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  );
};
